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
    def __init__(self, epics_id):
        """Initializes the Libera BPM device object and assigns it an ID. 
        
        Args:
            epics_id (str/int): The ID number assigned to that specific BPM device.
        Returns:
.
        """
        if type(epics_id) != str:  # Makes sure the ID is a string
            raise TypeError  # Raises a type error if integer is not used
        else:
            self.adc_n_bits = 12
            self.num_adcs = 4
            self.damage_level = 6  # The max power (dBm) the inputs can take before damage.
            self.switch_straight = 3  # The switch setting which corresponds to straight through.
            self.epics_id = epics_id  # TS-DI-EBPM-04:
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
            self.spec = self.get_performance_spec()
        print "Opened connection to " + self.device_id  # Informs the user the device is now connected to

    def __del__(self):
        """Informs the user that this object has been destroyed 
        
        Args:
        Returns:
         
        """
        LiberaBPM_common.write_epics_pv(self.epics_id, "FT:ENABLE_S", 'Disabled')#self.ft)
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN:AGC_S", self.agc)  # Restore AGC.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN:DISP_S", self.delta)  # Restore delta.
        # Restore attenuation waveform.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:ATTEN:OFFSET_S", self.attn_wfm)
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:AUTOSW_S", self.switches)  # Restore switches state.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:SETSW_S", self.switch_val)  # Restore switch setting.
        LiberaBPM_common.write_epics_pv(self.epics_id, "CF:DSC_S", self.dsc)  # Restore DSC setting.
        self.set_attenuation(self.attn)  # Restore attenuation setting.
        print "Closed connection to " + self.device_id

    def set_internal_state(self, state_dict):
        if 'agc' in state_dict.keys():
            agc = state_dict['agc']
        else:
            agc = 'AGC on'

        if 'delta'in state_dict.keys():
            delta = state_dict['delta']
        else:
            delta = 0

        if 'offset' in state_dict.keys():
            offset = state_dict['offset']
        else:
            offset = 0

        if 'switches' in state_dict.keys():
            switches = state_dict['switches']
        else:
            switches = 'Automatic'

        if 'switch_state' in state_dict.keys():
            switch_state = state_dict['switch_state']
        else:
            switch_state = 3

        if 'attenuation' in state_dict.keys():
            attenuation = state_dict['attenuation']
        else:
            attenuation = 0

        if 'dsc' in state_dict.keys():
            dsc = state_dict['dsc']
        else:
            dsc = 'Automatic'

        if 'ft_state' in state_dict.keys():
            ft_state = state_dict['ft_state']
        else:
            ft_state = 'Disabled'

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

    def get_internal_state(self):
        ft_state = LiberaBPM_common.read_epics_pv(self.epics_id, "FT:ENABLE_S")
        agc = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:ATTEN:AGC_S")  # Automatic gain control.
        delta = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:ATTEN:DISP_S")  # Set delta to zero.
        # Set attenuation waveform to offset.
        offset_wf = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:ATTEN:OFFSET_S")
        switches = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:AUTOSW_S")  # Set switches to manual.
        # Choose a switch setting to define a switch pattern.
        switch_state = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:SETSW_S")
        attenuation = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:ATTEN_S")  # Set initial attenuation
        dsc = LiberaBPM_common.read_epics_pv(self.epics_id, "CF:DSC_S")  # Set digital signal conditioning
        return ft_state, agc, delta, offset_wf, switches, switch_state, attenuation, dsc

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
        specs['noise_10kHz'] = ([0],
                                [0])
        specs['noise_1MHz'] = ([0],
                               [0])
        specs['Beam_current_dependence_X'] = ([0],
                                              [0])
        specs['Beam_current_dependence_Y'] = ([0],
                                              [0])
        specs['Beam_current_dependence_deviation_within_range_X'] = \
            ([[0, 0]],
             [   1])
        specs['Beam_current_dependence_deviation_within_range_Y'] = \
            ([[0, 0]],
             [   1])

        specs['Fill_pattern_dependence_X'] = ([0, 0], 0)
        specs['Fill_pattern_dependence_Y'] = ([0, 0], 0)

        specs['Beam_power_dependence_X'] = ([0],
                                            [0])
        specs['Beam_power_dependence_Y'] = ([0],
                                            [0])

        return specs
