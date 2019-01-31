from abc import ABCMeta, abstractmethod


class Generic_BPMDevice():
    """Generic BPM Device class used for hardware abstraction.

    All of the methods listed here are abstract and will be overridden by child classes, 
    this will abstract hardware as the methods here are called, but the functionality is 
    implemented by the individual children.

    Attributes:
    """

    __metaclass__ = ABCMeta  # Allows for abstract methods to be created.

    @abstractmethod
    def set_internal_state(self, state_dict):
        """Abstract method for override. Sets the internal state of the device.

        Args:
            state_dict (dict): Dictionary of parameters so set.
            """

    @abstractmethod
    def get_internal_state(self):
        """Abstract method for override. Returns the internal state of the device.

        Args:
        Returns: Parameters of the BPM settings
            """

    @abstractmethod
    def get_attenuation(self):
        """Abstract method for override, gets the calculated X position of the beam.

        Args:
        Returns:
            float: attenuation (dB)
        """
        pass

    @abstractmethod
    def set_attenuation(self, atten):
        """Abstract method for override, gets the calculated X position of the beam.

        Args:
            atten (float): Attenuation (dB)
        """
        pass

    @abstractmethod
    def get_x_position (self):
        """Abstract method for override, gets the calculated X position of the beam.
        
        Args:
        Returns: 
            float: X position in mm
        """
        pass

    @abstractmethod
    def get_y_position(self):
        """Abstract method for override, gets the calculated X position of the beam.
        
        Args:
        Returns: 
            float: Y position in mm
        """
        pass

    @abstractmethod
    def get_x_sa_data(self, num_vals):
        """Abstract method for override, gets the calculated X position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), X position in mm]
        """
        pass

    @abstractmethod
    def get_y_sa_data(self, num_vals):
        """Abstract method for override, gets the calculated Y position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), Y position in mm]
        """
        pass

    @abstractmethod
    def get_sa_data(self, num_vals):
        """Abstract method for override, gets the ABCD SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), Y position in mm]
        """
        pass

    @abstractmethod
    def get_tt_data(self):
        """Abstract method for override, gets the calculated X position TT data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), X position in mm]
        """
        pass

    @abstractmethod
    def get_adc_data(self, num_bits):
        """Abstract method for override, gets the ABCD ADC data.

        Args:
            num_bits (int): The number of bits the ADC has
        Returns: 
            list: [raw_timestamp (tuple), X position in mm]
        """
        pass

    @abstractmethod
    def get_ft_data(self):
        """Abstract method for override, gets the ABCD first turn data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), Y position in mm]
        """
        pass


    @abstractmethod
    def get_beam_current(self):
        """Abstract method for override, gets the beam current read by the BPMs. 
        
        Args:
        Returns: 
            float: Current in mA
        """
        pass

    @abstractmethod
    def get_input_power(self):
        """ Abstract method for override, gets the input power of the signals input to the device 
        
        Args:  
        Returns: 
            float: Input power in dBm
            
        """
        pass

    @abstractmethod
    def get_raw_bpm_buttons(self):
        """Abstract method for override, gets the raw signal from each BPM.
        
        Args:
        Returns: 
            
            int: Raw signal from BPM A
            int: Raw signal from BPM B
            int: Raw signal from BPM C
            int: Raw signal from BPM D
        """
        pass

    @abstractmethod
    def get_normalised_bpm_buttons(self):
        """Abstract method for override, gets the normalised signal from each BPM.
        
        Args:
        Returns: 
            float: Normalised signal from BPM A
            float: Normalised signal from BPM B
            float: Normalised signal from BPM C
            float: Normalised signal from BPM D
        """
        pass

    @abstractmethod
    def get_device_id(self):
        """Abstract method for override, gets the device name or type of the BPM.

        Args:
        Returns: 
            str: Type of BPM with MAC address
        """
        pass

    @abstractmethod
    def get_adc_sum(self):
        """Abstract method for override, gets the sum of all of the buttons ADCs
        
        A+B+C+D

        Args:
        Returns: 
            int: ADC sum in counts
        """
        pass

    @abstractmethod
    def get_performance_spec(self):
        """Abstract method for override, gets the factory performance specification data

                Args:
                Returns: 
                    dict: Various vectors of floats for different performance measures.
                """
        pass


