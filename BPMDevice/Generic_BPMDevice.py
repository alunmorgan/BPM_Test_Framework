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
    def get_X_position (self):
        """Abstract method for override, gets the calculated X position of the beam.
        
        Args:
        Returns: 
            float: X position in mm
        """
        pass

    @abstractmethod
    def get_Y_position(self):
        """Abstract method for override, gets the calculated X position of the beam.
        
        Args:
        Returns: 
            float: Y position in mm
        """
        pass

    @abstractmethod
    def get_X_SA_data(self, num_vals):
        """Abstract method for override, gets the calculated X position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), X position in mm]
        """
        pass

    @abstractmethod
    def get_Y_SA_data(self, num_vals):
        """Abstract method for override, gets the calculated Y position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), Y position in mm]
        """
        pass

    @abstractmethod
    def get_X_TT_data(self, num_vals):
        """Abstract method for override, gets the calculated X position TT data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), X position in mm]
        """
        pass

    @abstractmethod
    def get_Y_TT_data(self, num_vals):
        """Abstract method for override, gets the calculated Y position TT data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), Y position in mm]
        """
        pass

    @abstractmethod
    def get_X_ADC_data(self, num_vals):
        """Abstract method for override, gets the calculated X position ADC data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), X position in mm]
        """
        pass

    @abstractmethod
    def get_Y_ADC_data(self, num_vals):
        """Abstract method for override, gets the calculated Y position ADC data.

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
    def get_raw_BPM_buttons(self):
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
    def get_normalised_BPM_buttons(self):
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
    def get_device_ID(self):
        """Abstract method for override, gets the device name or type of the BPM.

        Args:
        Returns: 
            str: Type of BPM with MAC address
        """
        pass

    @abstractmethod
    def get_input_tolerance(self):
        """Abstract method for override, gets the maximum input power the device can take

        Args:
        Returns: 
            float: max input power in dBm
        """
        pass

    @abstractmethod
    def get_ADC_sum(self):
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



