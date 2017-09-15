from Generic_BPMDevice import *
#import sys, os
#sys.path.insert(0, os.path.abspath('..'))
from pkg_resources import require
require("numpy")
import numpy as np


class Simulated_BPMDevice(Generic_BPMDevice):
    """Simulated BPM device used for testing without the hardware. 

    All of the abstract methods in the parent class must be overridden. This class has
    access to the RF device used in the testing so that it can read in the signals that
    are supposedly provided to it via it's RF inputs. 

    Attributes:
        attenuation (float): Attenuation produced by the virtual splitter and cables
        RFSim (RF Simulator Obj) : Reference to an RF simulator 
        GateSim (Gate Source Simulator Obj) : Reference to a gate source simulator
    """

    def __init__(self, RFSim, gatesim=None, progatten=None):
        """Initializes the Libera BPM device object and assigns it an ID. 
        
        Args:
            RFSim (RFSignalGenerator Obj): The interface object that has access to an RF device 
                this is needed in the simulator so it can access the input values that would 
                normally come through the signals supplied to the devices inputs.
            gatesim (Gate_Source Object): The interface object that has access to a Gate Source
                device. This will typically be a simulated GateSource, this is an input to this 
                class so it know what signals are being sent to it. 
            progatten (Programmable attenuator Object): The interface object that has access to a programmable attenuator
                device. This will typically be a simulated GateSource, this is an input to this 
                class so it know how much signals are being attenuated between the RF source and it. 
        Returns: 
            
        """
        print("Simulated BPM device accessed on virtual channel")
        self.attenuation = 12  # Typical attenuation when using a 4 way splitter and cables
        self.RFSim = RFSim  # Instance of the RF source used, allows the simulator to know what signals are output
        self.GateSim = gatesim  # Instance of the Gate device, allows the simulator to know what signals are output
        self.ProgAtten = progatten # Instance of the Programmable attenuator, allows to know about changes to input levels.
        self.macaddress = 'SIMULATED'

    def get_X_position(self):
        """Override method, gets the calculated X position of the beam.
        
        Args:
        
        Returns: 
            float: X position in mm
        """
        if self.ProgAtten is None:
            x_val = 0.0 # With an equal splitter there should be no X shift
        else:
            A_pwr, B_pwr, C_pwr, D_pwr = self.attenuate_inputs(self.RFSim.get_output_power()[0])
            total_power = A_pwr + B_pwr + C_pwr + D_pwr
            x_val = ((A_pwr + D_pwr) - (B_pwr + C_pwr)) / total_power
        return x_val * 10  # Scaling to mm

    def get_Y_position(self):
        """Override method, gets the calculated X position of the beam.
        
        Args:
        
        Returns: 
            float: Y position in mm
        """
        if self.ProgAtten is None:
            y_val = 0.0  # With an equal splitter there should be no Y shift
        else:
            A_pwr, B_pwr, C_pwr, D_pwr = self.attenuate_inputs(self.RFSim.get_output_power()[0])
            total_power = A_pwr + B_pwr + C_pwr + D_pwr
            y_val = ((A_pwr + B_pwr) - (C_pwr + D_pwr)) / total_power
            print y_val
        return y_val * 10  # Scaling to mm

    def get_beam_current(self):
        """Override method, gets the beam current read by the BPMs. 
        
        By measuring the output power from the RF device, the input power can be assumed, then an equation extracted
        from the Rigol 30303 and Libera BPM device can be used to give an estimate of the current. 
        
        Args:
            
        Returns: 
            float: Current in mA
        """
        current = self.get_input_power()  # Gets the current input power
        current = 1000 * (1.1193) ** current # Extracted equation from Rigol3030 vs Libera BPM measurements
        return current

    def get_input_power(self):
        """Override method, gets the input power of the signals input to the device 
        
        If a RF gate is setup then the RF power from the source will be reduced by the duty cycle.
        If a programmable attenuator is setup then the additional attenuation is added to the static 12dB loss.
        In the absence of a programmable attenuator, this function assumes that a standard 4 way splitter is used, 
        that combined with the cable losses give an estimated loss of 12 dB. 
        This is then taken off of the output power set by the RF device giving the result. 
        
        Args:
        
        Returns: 
            float: Input power in dBm
        """

        power_total = self.RFSim.get_output_power()[0]  # Gets the power output by the RF, total power into the system

        if self.GateSim is not None and self.GateSim.get_modulation_state() is not False:
            # gate source is present and enabled
            dutycycle = self.GateSim.get_pulse_dutycycle()  # Get the current duty cycle
            log_cycle = 20 * np.log10(dutycycle)  # Convert the duty cycle into dB
            # factor the duty cycle into the power read by the simulated BPM
            power_total = power_total - np.absolute(log_cycle)

        if self.ProgAtten is not None:
            A_pwr, B_pwr, C_pwr, D_pwr = self.attenuate_inputs(power_total)
            # Total power into the BPM after each signal is attenuated (dBm)
            power_total = 10 * np.log10(A_pwr + B_pwr + C_pwr + D_pwr)

        return power_total - self.attenuation

    def get_raw_BPM_buttons(self):
        """Override method, gets the raw signal from each BPM.
        
        Args:
            
        Returns: 
            int: Raw signal from BPM A
            int: Raw signal from BPM B
            int: Raw signal from BPM C
            int: Raw signal from BPM D
        """
        ADC = 1000 * self.get_beam_current()  # Gets a linear value for the BPM
        if self.ProgAtten is None:
            raw_A = raw_B = raw_C = raw_D = ADC
        else:
            A_pwr, B_pwr, C_pwr, D_pwr = self.attenuate_inputs(self.RFSim.get_output_power()[0])
            total_power = A_pwr + B_pwr + C_pwr + D_pwr
            raw_A = A_pwr / total_power * ADC
            raw_B = B_pwr / total_power * ADC
            raw_C = C_pwr / total_power * ADC
            raw_D = D_pwr / total_power * ADC

        return raw_A, raw_B, raw_C, raw_D

    def get_normalised_BPM_buttons(self):
        """Override method, gets the normalised signal from each BPM.
        
        Args:
        
        Returns: 
            float: Normalised signal from BPM A
            float: Normalised signal from BPM B
            float: Normalised signal from BPM C
            float: Normalised signal from BPM D
        """
        if self.ProgAtten is None:
            norm_A = norm_B = norm_C = norm_D = 1
        else:
            A_pwr, B_pwr, C_pwr, D_pwr = self.attenuate_inputs(self.RFSim.get_output_power()[0])
            total_power = A_pwr + B_pwr + C_pwr + D_pwr
            # The *4 is to get back to normalised channels rather than normalise to the total power.
            norm_A = A_pwr / total_power * 4
            norm_B = B_pwr / total_power * 4
            norm_C = C_pwr / total_power * 4
            norm_D = D_pwr / total_power * 4
        return norm_A, norm_B, norm_C, norm_D  # Assumes all BPM pickups are equal

    def get_device_ID(self):
        """Override method, gets the type of BPM device that the device is
        
        Args:
        
        Returns: 
            str: Device type 
        """
        return "Simulated BPM Device"

    def get_ADC_sum(self):
        """Override method, sum of the raw signals

        Returns the sum signal, comprised of the sum of all four raw ADC channels.        

        Args:
        Returns: 
            int: Total ADC counts
        """
        a, b, c, d = self.get_raw_BPM_buttons()
        ADC_sum = a + b + c + d  # Sums the BPM values used in the simulator
        return ADC_sum

    def get_input_tolerance(self):
        """Override method, gets the maximum input power the device can take

        The devices will break if the input power is too high, as such, each device has their
        own tolerances, this function will return this tolerance. It should be used to ensure 
        that the power put into the device is not too high to break the device. 

        Args:

        Returns: 
            float: max input power in dBm
        """
        return -40  # Max tolerance of the simulated device, as low as the most susceptible real device

    def attenuate_inputs(self, power_total):
        A_atten, B_atten, C_atten, D_atten = self.ProgAtten.get_global_attenuation()

        # The power delivered into each BPM input after passing through the attenuator.
        # Assuming no losses through cables etc...
        # converted into mW
        A_pwr = 10 ** ((power_total - 6 - A_atten) / 10)
        B_pwr = 10 ** ((power_total - 6 - B_atten) / 10)
        C_pwr = 10 ** ((power_total - 6 - C_atten) / 10)
        D_pwr = 10 ** ((power_total - 6 - D_atten) / 10)
        return A_pwr, B_pwr, C_pwr, D_pwr

    def get_performance_spec(self):
        """Override method, gets the factory performance specifications.
    
        In order to determine pass/fail criteria, one needs to have something to compare to. 
        This function returns the factory specification data ready for comparison.
    
        The following results are present: All results are in um.
        Noise measurements:
            'noise_10kHz' (fs=10kHz, BW=2kHz, DSC=on, AGC=off)
            'noise_1MHz' (fs=1MHz(TBT), BW=0.3*fs, DSC=off, AGC=off)
        Beam power dependence: Input is power at the Libera input
            'Beam_power_dependence_X' (fs=10kHz, DSC=on, AGC=off)
            'Beam_power_dependence_Y' (fs=10kHz, DSC=on, AGC=off)
            'Beam_power_dependence_deviation_within_range_X' (fs=10kHz, DSC=on, AGC=off)
            'Beam_power_dependence_deviation_within_range_Y' (fs=10kHz, DSC=on, AGC=off)
        Fill pattern dependence: (Constant input power of -10dBm at libera input)
            'Fill_pattern_dependence_X' (T=1/fs, fs=10kHz, DSC=on, AGC=off)
            'Fill_pattern_dependence_Y' (T=1/fs, fs=10kHz, DSC=on, AGC=off)
    
        Args:
        Returns: 
            dict: a set of vectors containing comparison data
        """
        specs = {}
        specs['noise_10kHz'] = ([0,   -24, -24, -32, -32, -40, -40, -44, -44, -50, -50, -56, -56, -62, -62, -68, -68, -74, -74, -80, -80],
                                [0.2, 0.2, 0.3, 0.3, 0.5, 0.5,  1,   1,   2,   2,   4,   4,   5,   5,   10,  10,  20,  20,  50,  50, 100])
        specs['noise_1MHz'] = ([0, -32, -32, -36, -36, -40, -40, -44, -44, -50, -50, -56, -56, -62, -62, -68, -68, -74, -74, -80, -80],
                               [3,  3,   5,   5,   6,   6,   8,   8,   15,  15,  30,  30,  50,  50, 150, 150, 300, 300, 600, 600, 1500])
        specs['Beam_power_dependence_X'] = ([0, -2, -2, -56, -56, -68, -68, -74, -74, -80, -80],
                                            [0,  0,  1,  1,   2,   2,   10,  10,  20,  20,  50])
        specs['Beam_power_dependence_Y'] = ([0, -2, -2, -56, -56, -68, -68, -74, -74, -80, -80],
                                            [0,  0,  1,  1,   2,   2,   10,  10,  20,  20,  50])
        specs['Beam_power_dependence_deviation_within_range_X'] = \
            ([[0, -8], [-8, -20], [-20, -32], [-32, -40], [-40, -56], [-56, -68], [-68, -70]],
             [1, 1, 1, 1, 1, 5, 50])
        specs['Beam_power_dependence_deviation_within_range_Y'] = \
            ([[0, -8], [-8, -20], [-20, -32], [-32, -40], [-40, -56], [-56, -68], [-68, -70]],
             [1, 1, 1, 1, 1, 5, 50])

        specs['Fill_pattern_dependence_X'] = ([20, 100], 1)
        specs['Fill_pattern_dependence_Y'] = ([20, 100], 1)

        return specs
