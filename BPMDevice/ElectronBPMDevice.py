from pkg_resources import require
require("cothread==2.14")
from cothread.catools import caget, caput, connect
#import cothread
from Generic_BPMDevice import *
from subprocess import Popen, PIPE
import numpy as np
from BPM_helper_functions import Accumulator
import time


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

    def _read_epics_pv(self, pv):
        """Private method to read an Epics process variable.
        
        Wraps up caget call, makes it easy for multiple reads to be programmed 
        and a timeout added if required. 
        
        Args:
            pv (str): Name of the Epics process variable to read.  
        Returns: 
            variant: Value of requested process variable.
        """
        return caget(''.join((self.epics_id, pv)))  # Get PV data

    def _write_epics_pv(self, pv, val):
        """Private method to write to an Epics process variable.

        Wraps up caget call, makes it easy for multiple reads to be programmed 
        and a timeout added if required. 

        Args:
            pv (str): Name of the Epics process variable to read. 
            val (str, int, float): Value to write to the process variable.
        Returns: 
            variant: Value of requested process variable.
        """
        return caput(''.join((self.epics_id, pv)), val)  # Write PV data

    def _get_mac_address(self):
        pv = "SA:X"  # Any PV hosts on the device could be used here
        node = connect(self.epics_id + pv, cainfo=True).host.split(":")[0]  # Get the IP address of the host
        host_info = Popen(["arp", "-n", node], stdout=PIPE).communicate()[0]  # Uses arp to get more info about the host
        host_info = host_info.split("\n")[1]  # Splits the data about the host
        index = host_info.find(":")  # Gets the first ":", used in the MAC address
        host_info = host_info[index - 2:index + 15]  # Gets the devices MAC address
        return host_info

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
            self.adc_n_bits = 16
            self.num_adcs = 4
            self.epics_id = dev_id # TS-DI-EBPM-04:
            self.mac_address = self._get_mac_address()
            self.device_id = self.get_device_id()
            # Initial setup of the BPM system.
            self.ft = self._read_epics_pv("FT:ENABLE_S")
            self.kx = self._read_epics_pv("CF:KX_S")
            self.ky = self._read_epics_pv("CF:KY_S")
            self.agc = self._read_epics_pv("CF:ATTEN:AGC_S")
            self.delta = self._read_epics_pv("CF:ATTEN:DISP_S")
            self.attn_wfm = self._read_epics_pv("CF:ATTEN:OFFSET_S")
            self.switches = self._read_epics_pv("CF:AUTOSW_S")
            self.switch_val = self._read_epics_pv("CF:SETSW_S")
            self.attn = self.get_attenuation()
            self.dsc = self._read_epics_pv("CF:DSC_S")
        print "Opened connection to " + self.device_id  # Informs the user the device is now connected to

    def __del__(self):
        """Informs the user that this object has been destroyed 
        
        Args:
        Returns:
         
        """
        # restore the BPM system.
        if self.agc == 0:
            agc = 'AGC off'
        elif self.agc == 1:
            agc = 'AGC on'
        else:
            raise IOError('AGC value is invalid')
        self._write_epics_pv("FT:ENABLE_S", self.ft)
        self._write_epics_pv("CF:ATTEN:AGC_S", agc)  # Restore AGC.
        self._write_epics_pv("CF:ATTEN:DISP_S", self.delta)  # Restore delta.
        self._write_epics_pv("CF:ATTEN:OFFSET_S", self.attn_wfm)  # Restore attenuation waveform.
        self._write_epics_pv("CF:AUTOSW_S", self.switches)  # Restore switches state.
        self._write_epics_pv("CF:SETSW_S", self.switch_val)  # Restore switch setting.
        self._write_epics_pv("CF:DSC_S", self.dsc)  # Restore DSC setting.
        self.set_attenuation(self.attn)  # Restore attenuation setting.
        print "Closed connection to " + self.get_device_id()

    def set_internal_state(self, agc='AGC off', delta=0, offset=0, switches='Auto',
                           switch_state=15, attenuation=0, dsc='Automatic',
                           ft_state='Disabled'):
        """Sets up the internal state of the BPM. The defaults set it up in normal running conditions."""
        self._write_epics_pv("FT:ENABLE_S", ft_state)
        self._write_epics_pv("CF:ATTEN:AGC_S", agc)  # Set Automatic gain control.
        self._write_epics_pv("CF:ATTEN:DISP_S", delta)  # Set delta to zero.
        # Set attenuation waveform to offset.
        self._write_epics_pv("CF:ATTEN:OFFSET_S", [x * offset for x in np.ones_like(self.attn_wfm)])
        self._write_epics_pv("CF:AUTOSW_S", switches)  # Set switches to manual.
        self._write_epics_pv("CF:SETSW_S", switch_state)  # Choose a switch setting to define a switch pattern.
        self._write_epics_pv("CF:ATTEN_S", attenuation)  # Set initial attenuation
        self._write_epics_pv("CF:DSC_S", dsc)  # Set digital signal conditioning

    def get_attenuation(self):
        """Override method, gets the internal attenuation setting.


                Returns:
                    float: Attenuation (dB)
                    """
        return self._read_epics_pv("CF:ATTEN_S")

    def set_attenuation(self, attn):
        """Override method, sets the internal attenuation setting.


                Args:
                    attn (float): Attenuation (dB)
                    """
        self._write_epics_pv("CF:ATTEN_S", attn)

    def get_x_position(self):
        """Override method, gets the calculated X position of the beam.
        
        Args:   
        Returns: 
            float: X position in mm
        """
        return self._read_epics_pv("SA:X")  # Reads the requested PV

    def get_y_position(self):
        """Override method, gets the calculated Y position of the beam.
        
        Args:  
        Returns: 
            float: Y position in mm
        """
        return self._read_epics_pv("SA:Y")  # Reads the requested PV

    def get_x_sa_data(self, num_vals):
        """Gets the calculated X position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            timestamps (list): floats
            data (list): floats
        """
        sa_x_accum = Accumulator(''.join((self.epics_id, 'SA:X')), num_vals)
        times, data = sa_x_accum.wait()
        times_rel = [x - times[0] for x in times]
        return times_rel, data

    def get_y_sa_data(self, num_vals):
        """Gets the calculated X position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            timestamps (list): floats
            data (list): floats
        """
        sa_y_accum = Accumulator(''.join((self.epics_id, 'SA:Y')), num_vals)
        times, data = sa_y_accum.wait()
        times_rel = [x - times[0] for x in times]
        return times_rel, data

    def get_sa_data(self, num_vals):
        """Gets the ABCD SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            timestamps (list): floats
            data (list): floats
        """
        sa_a_accum = Accumulator(''.join((self.epics_id, 'SA:A')), num_vals)
        sa_a_times, sa_a_data = sa_a_accum.wait()
        sa_b_accum = Accumulator(''.join((self.epics_id, 'SA:B')), num_vals)
        sa_b_times, sa_b_data = sa_b_accum.wait()
        sa_c_accum = Accumulator(''.join((self.epics_id, 'SA:C')), num_vals)
        sa_c_times, sa_c_data = sa_c_accum.wait()
        sa_d_accum = Accumulator(''.join((self.epics_id, 'SA:D')), num_vals)
        sa_d_times, sa_d_data = sa_d_accum.wait()

        return sa_a_times, sa_a_data, sa_b_times, sa_b_data, sa_c_times, sa_c_data, sa_d_times, sa_d_data

    def get_tt_data(self):
        """ Gets the calculated ABCD TT data.

        Args:
            num_vals (int): The number of samples to capture
       Returns: 
            times (list): floats
            data (list): floats
        """
        self._write_epics_pv('TT:CAPLEN_S', 131072)
        self._write_epics_pv('TT:DELAY_S', 0)
        self._write_epics_pv('TT:ARM', 1)
        data1 = self._read_epics_pv("TT:WFA")
        data2 = self._read_epics_pv("TT:WFA")
        data3 = self._read_epics_pv("TT:WFA")
        data4 = self._read_epics_pv("TT:WFA")

        times = np.arange(len(data1)) * 936./500e6 # Each tick is one turn
        return times, data1, data2, data3, data4

    def get_adc_data(self):
        """ Gets the ABCD ADC data.

        Returns: 
            timestamps (list): floats
            adc1_data (list): floats
            adc2_data (list): floats
            adc3_data (list): floats
            adc4_data (list): floats
        """
        self._write_epics_pv('FT:ENABLE_S', 1)
        time.sleep(1)
        adc1_data = self._read_epics_pv('FT:RAW1')
        adc2_data = self._read_epics_pv('FT:RAW2')
        adc3_data = self._read_epics_pv('FT:RAW3')
        adc4_data = self._read_epics_pv('FT:RAW4')
        time.sleep(1)
        self._write_epics_pv('FT:ENABLE_S', 0)
        # The data is centred on the middle bits. Shift it so all values are positive.
        num_bits = 16
        half_range = np.power(2, num_bits) / 2
        adc1_data[:] = [x + half_range for x in adc1_data]
        adc2_data[:] = [x + half_range for x in adc2_data]
        adc3_data[:] = [x + half_range for x in adc3_data]
        adc4_data[:] = [x + half_range for x in adc4_data]
        times = np.arange(len(adc1_data)) * 1/117E6  # Data rate is 117MHz
        return list(times), list(adc1_data), list(adc2_data), list(adc3_data), list(adc4_data)

    def get_ft_data(self):
        """ Gets the ABCD first turn data.

        Args:
            num_vals (int): The number of samples to capture
       Returns: 
            timestamps (list): floats
            data (list): floats
        """
        self._write_epics_pv('FT:ENABLE_S', 1)
        fta_data = self._read_epics_pv(':WFA')
        ftb_data = self._read_epics_pv(':WFB')
        ftc_data = self._read_epics_pv(':WFC')
        ftd_data = self._read_epics_pv(':WFD')
        self._write_epics_pv('FT:ENABLE_S', 0)
        times = np.arange(len(fta_data)) * 1/30E6 # Data rate is 30MHz
        return times, fta_data, ftb_data, ftc_data, ftd_data

    def get_beam_current(self):
        """Override method, gets the beam current read by the BPMs. 
        
        Args:
        Returns: 
            float: Current in mA
        """
        return self._read_epics_pv("SA:CURRENT")  # Reads the requested PV

    def get_input_power(self):
        """Override method, gets the input power of the signals input to the device 
        
        Args:
        Returns: 
            float: Input power in dBm
        """
        return self._read_epics_pv("SA:POWER")  # Reads the requested PV

    def get_raw_bpm_buttons(self):
        """Override method, gets the raw signal from each BPM.
        
        Args: 
        Returns: 
            float: Raw signal from BPM A
            float: Raw signal from BPM B
            float: Raw signal from BPM C
            float: Raw signal from BPM D
        """
        return (self._read_epics_pv("SA:A"),
                self._read_epics_pv("SA:B"),
                self._read_epics_pv("SA:C"),
                self._read_epics_pv("SA:D"))  # Reads the requested PVs

    def get_normalised_bpm_buttons(self):
        """Override method, gets the normalised signal from each BPM.
        
        Args: 
        Returns: 
            float: Normalised signal from BPM A
            float: Normalised signal from BPM B
            float: Normalised signal from BPM C
            float: Normalised signal from BPM D
        """
        return (self._read_epics_pv("SA:AN"),
                self._read_epics_pv("SA:BN"),
                self._read_epics_pv("SA:CN"),
                self._read_epics_pv("SA:DN"))  # Reads the requested PVs

    def get_adc_sum(self):
        """Override method, gets the sum of all of the buttons ADCs

        A+B+C+D

        Args:
        Returns: 
            int: ADC sum in counts
        """
        a, b, c, d = self.get_raw_bpm_buttons()  # Reads the requested PVs
        sum = a + b + c + d  # Sums the values of the PVs
        return sum

    def get_device_id(self):
        """Override method, gets the device's epics ID and MAC address 
        
        Args:
        Returns: 
            str: Device with epics channel ID and MAC address
        """

        return "Libera Electron BPM with the Epics ID " + "\"" + self.epics_id + \
               "\" and the MAC Address \"" + self.mac_address + "\""

    def get_input_tolerance(self):
        """Override method, gets the maximum input power the device can take

        The devices will break if the input power is too high, as such, each device has their
        own tolerances, this function will return this tolerance. It should be used to ensure 
        that the power put into the device is not too high to break the device. 

        Args:
        Returns: 
            float: max input power in dBm
        """
        return -20 # The maximum continuous input power the Electron can handle in dBm

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

