from Generic_BPMDevice import *
import LiberaBPM_common
import numpy as np


class ElectronBPMDevice(Generic_BPMDevice):
    """Libera Electron BPM Device class that uses Epics to communicate with PVs.

    All of the methods here will attempt to be generic enough to work for Libera
    devices that have the same PV names. If these names change, then a different 
    class will have to be used. Most data is acquired using the slow acquisition 
    method as the tests are not intensive, for noise tests and the such, direct 
    access to the data buffers may be needed. 

    Attributes:
        epics_id (str): Channel identifier string that will be used to access PVs.
    """
    def __init__(self, dev_id):
        """Initializes the Libera BPM device object and assigns it an ID. 
        
        Args:
            dev_id (str/int): The ID number assigned to that specific BPM device.
        Returns:
.
        """
        if type(dev_id) != str:  # Makes sure the ID is a string
            raise TypeError  # Raises a type error if integer is not used
        else:
            self.adc_n_bits = 12
            self.num_adcs = 4
            self.max_input = 6  # The max power (dBm) the inputs can take before damage.
            self.switch_straight = 3  # The switch setting which corresponds to straight through.
            self.epics_id = dev_id  # TS-DI-EBPM-04:
            self.mac_address = LiberaBPM_common.get_mac_address(self.epics_id)
            self.device_id = self.get_device_id()
            # Initial setup of the BPM system.
            self.ft = LiberaBPM_common.read_epics_pv(self.epics_id, "FT:ENABLE_S")
            self.kx = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:KX_S")
            self.ky = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:KY_S")
            self.agc = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:ATTEN:AGC_S")
            self.delta = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:ATTEN:DISP_S")
            self.attn_wfm = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:ATTEN:OFFSET_S")
            self.switches = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:AUTOSW_S")
            self.switch_val = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:SETSW_S")
            self.attn = self.get_attenuation()
            self.dsc = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:DSC_S")
        print "Opened connection to " + self.device_id  # Informs the user the device is now connected to

    def __del__(self):
        """Informs the user that this object has been destroyed 
        
        Args:
        Returns:
         
        """
        print 'Restoring FT state to', self.ft
        LiberaBPM_common.write_epics_pv(self.epics_id, "FT:ENABLE_S", 'Disabled')#self.ft)
        print 'Restored FT state'
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN:AGC_S", self.agc)  # Restore AGC.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN:DISP_S", self.delta)  # Restore delta.
        # Restore attenuation waveform.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN:OFFSET_S", self.attn_wfm)
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:AUTOSW_S", self.switches)  # Restore switches state.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:SETSW_S", self.switch_val)  # Restore switch setting.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:DSC_S", self.dsc)  # Restore DSC setting.
        self.set_attenuation(self.attn)  # Restore attenuation setting.
        print "Closed connection to " + self.device_id

    def set_internal_state(self, agc='AGC on', delta=0, offset=0, switches='Auto',
                           switch_state=3, attenuation=0, dsc='Automatic',
                           ft_state='Disabled'):
        """Sets up the internal state of the BPM. The defaults set it up in normal running conditions."""
        LiberaBPM_common.write_epics_pv(self.epics_id, "FT:ENABLE_S", ft_state)
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN:AGC_S", agc)  # Set Automatic gain control.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN:DISP_S", delta)  # Set delta to zero.
        # Set attenuation waveform to offset.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN:OFFSET_S", offset * np.ones_like(self.attn_wfm))
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:AUTOSW_S", switches)  # Set switches to manual.
        # Choose a switch setting to define a switch pattern.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:SETSW_S", switch_state)
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN_S", attenuation)  # Set initial attenuation
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:DSC_S", dsc)  # Set digital signal conditioning

    def get_attenuation(self):
        """Override method, gets the internal attenuation setting.


                Returns:
                    float: Attenuation (dB)
                    """
        return LiberaBPM_common.get_attenuation(self.epics_id)

    def set_attenuation(self, attn):
        """Override method, sets the internal attenuation setting.


                Args:
                    attn (float): Attenuation (dB)
                    """
        LiberaBPM_common.set_attenuation(self.epics_id, attn)

    def get_x_position(self):
        """Override method, gets the calculated X position of the beam.
        
        Args:   
        Returns: 
            float: X position in mm
        """
        return LiberaBPM_common.get_x_position(self.epics_id)

    def get_y_position(self):
        """Override method, gets the calculated Y position of the beam.
        
        Args:  
        Returns: 
            float: Y position in mm
        """
        return LiberaBPM_common.get_y_position(self.epics_id)

    def get_x_sa_data(self, num_vals):
        """Gets the calculated X position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            timestamps (list): floats
            data (list): floats
        """
        return LiberaBPM_common.get_x_sa_data(self.epics_id, num_vals)

    def get_y_sa_data(self, num_vals):
        """Gets the calculated X position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            timestamps (list): floats
            data (list): floats
        """
        return LiberaBPM_common.get_y_sa_data(self.epics_id, num_vals)

    def get_sa_data(self, num_vals):
        """Gets the ABCD SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            timestamps (list): floats
            data (list): floats
        """
        return LiberaBPM_common.get_sa_data(self.epics_id, num_vals)

    def get_tt_data(self):
        """ Gets the calculated ABCD TT data.

        Args:
       Returns:
            times (list): floats
            data (list): floats
        """
        return LiberaBPM_common.get_tt_data(self.epics_id)

    def get_adc_data(self, num_bits):
        """ Gets the ABCD ADC data.

        Returns: 
            timestamps (list): floats
            adc1_data (list): floats
            adc2_data (list): floats
            adc3_data (list): floats
            adc4_data (list): floats
        """
        return LiberaBPM_common.get_adc_data(self.epics_id, num_bits)

    def get_ft_data(self):
        """ Gets the ABCD first turn data.

        Args:
       Returns:
            timestamps (list): floats
            data (list): floats
        """
        return LiberaBPM_common.get_ft_data(self.epics_id)

    def get_beam_current(self):
        """Override method, gets the beam current read by the BPMs. 
        
        Args:
        Returns: 
            float: Current in mA
        """
        return LiberaBPM_common.get_beam_current(self.epics_id)

    def get_input_power(self):
        """Override method, gets the input power of the signals input to the device 
        
        Args:
        Returns: 
            float: Input power in dBm
        """
        return LiberaBPM_common.get_input_power(self.epics_id)

    def get_raw_bpm_buttons(self):
        """Override method, gets the raw signal from each BPM.
        
        Args: 
        Returns: 
            float: Raw signal from BPM A
            float: Raw signal from BPM B
            float: Raw signal from BPM C
            float: Raw signal from BPM D
        """
        return LiberaBPM_common.get_raw_bpm_buttons(self.epics_id)

    def get_normalised_bpm_buttons(self):
        """Override method, gets the normalised signal from each BPM.
        
        Args: 
        Returns: 
            float: Normalised signal from BPM A
            float: Normalised signal from BPM B
            float: Normalised signal from BPM C
            float: Normalised signal from BPM D
        """
        return LiberaBPM_common.get_normalised_bpm_buttons(self.epics_id)

    def get_adc_sum(self):
        """Override method, gets the sum of all of the buttons ADCs

        A+B+C+D

        Args:
        Returns: 
            int: ADC sum in counts
        """
        return LiberaBPM_common.get_adc_sum(self.epics_id)

    def get_device_id(self):
        """Override method, gets the device's epics ID and MAC address 
        
        Args:
        Returns: 
            str: Device with epics channel ID and MAC address
        """

        return "Libera Electron BPM with the Epics ID " + "\"" + self.epics_id + \
               "\" and the MAC Address \"" + self.mac_address + "\""

    # def get_input_tolerance(self):
    #     """Override method, gets the maximum input power the device can take
    #
    #     The devices will break if the input power is too high, as such, each device has their
    #     own tolerances, this function will return this tolerance. It should be used to ensure
    #     that the power put into the device is not too high to break the device.
    #
    #     Args:
    #     Returns:
    #         float: max input power in dBm
    #     """
    #     return 6  # The maximum continuous input power the Electron can handle in dBm

    def get_performance_spec(self):
        """Override method, gets the factory performance specifications.

        In order to determine pass/fail criteria, one needs to have something to compare to. 
        This function returns the factory specification data ready for comparison.

        The following results are present: All results are in um.
        Noise measurements:
            'noise_10kHz' (fs=10kHz, BW=2kHz, DSC=on, AGC=off)
            'noise_1MHz' (fs=1MHz(TBT), BW=0.3*fs, DSC=off, AGC=off)
        Beam current dependence: Input is power at the Libera input
            'Beam_current_dependence_X' (fs=10kHz, DSC=on, AGC=off)
            'Beam_current_dependence_Y' (fs=10kHz, DSC=on, AGC=off)
            'Beam_current_dependence_deviation_within_range_X' (fs=10kHz, DSC=on, AGC=off)
            'Beam_current_dependence_deviation_within_range_Y' (fs=10kHz, DSC=on, AGC=off)
        Fill pattern dependence: (Constant input power of -10dBm at libera input)
            'Fill_pattern_dependence_X' (T=1/fs, fs=10kHz, DSC=on, AGC=off)
            
        Args:
        Returns: 
            dict: a set of vectors containing comparison data
        """
        specs ={}
        specs['noise_10kHz'] = ([0,  -24, -32, -40, -44, -50, -56, -62, -68, -74, -80],
                                [0.2, 0.3, 0.5, 1,   2,   4,   5,   10,  20,  50, 100])
        specs['noise_1MHz'] = ([0, -32, -36, -40, -44, -50, -56, -62, -68, -74, -80],
                               [3,  5,   6,   8,   15,  30,  50,  150, 300, 600, 1500])
        specs['Beam_current_dependence_X'] = ([0, -2, -56, -68, -74, -80],
                                              [0,  1,   2,  10,  20,  50])
        specs['Beam_current_dependence_Y'] = ([0, -2, -56, -68, -74, -80],
                                              [0,  1,   2,  10,  20,  50])
        specs['Beam_current_dependence_deviation_within_range_X'] = \
            ([[0, -8], [-8, -20], [-20, -32], [-32, -40], [-40, -56], [-56, -68], [-68, -70]],
             [   1,        1,          1,          1,          1,          5,          50])
        specs['Beam_current_dependence_deviation_within_range_Y'] = \
            ([[0, -8], [-8, -20], [-20, -32], [-32, -40], [-40, -56], [-56, -68], [-68, -70]],
             [   1,        1,          1,          1,          1,          5,          50])

        specs['Fill_pattern_dependence_X'] = ([20, 100], 1)
        specs['Fill_pattern_dependence_Y'] = ([20, 100], 1)

        specs['Beam_power_dependence_X'] = ([0, -2, -56, -68, -74, -80],
                                            [0,  1,   2,  10,  20,  50])
        specs['Beam_power_dependence_Y'] = ([0, -2, -56, -68, -74, -80],
                                            [0,  1,   2,  10,  20,  50])

        return specs

