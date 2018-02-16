from abc import ABCMeta, abstractmethod


class Generic_TrigSource():
    """Generic waveform generator class used for hardware abstraction.

    All of the methods listed here are abstract and will be overridden by child classes, 
    this will abstract hardware as the methods here are called, but the functionality is 
    implemented by the individual children.

    Attributes:
        Output_Power (float/str): The output power of the RF SigGen. As a float default units will be 
            dBm, using a string new units can be selected. 
        Frequency (float/str): The frequency output from the RF SigGen. As a float default units will be 
            MHz, using a string new units can be selected. 
        Output_state (bool): RF output enabled flag.
        DeviceID (str): The specific ID or model of the SigGen.
    """
    __metaclass__ = ABCMeta  # Allows for abstract methods to be created.

    Output_Power = "0DBM"
    Frequency = "0DBM"
    Output_State = False
    DeviceID = 'Abstract Device Class'

    def _split_num_char(self, s):
        """Private method to split up a numeric and characters. 

        This should be used to split a value with it's units into two separate strings.
        i.e. "-70.5 dBm" will return "-70.5" and "dBm" separately. 

        Args:
            s (str): The string that is to be disseminated.

        Returns:
            str: The numeric characters in the string provided.  
            str: The non numeric characters in the string provided. 
        """

        number = ''
        unit = ''
        s = str(s)
        for c in s:
            if c.isdigit() or c == "." or c == "-":
                number += c
            else:
                unit += c

        return (number, unit)

    @abstractmethod
    def get_device_id(self):
        """Abstract method for override that will return device ID.

        Returns:
            str: The DeviceID of the SigGen.
        """
        pass

    @abstractmethod
    def set_up_trigger_pulse(self, frequency):
        """Abstract method for override that will set up the generator to output s series of pulses to be used as a trigger.

        Args:
            frequency (float): Desired value of the output frequency. 
        """
        pass

    @abstractmethod
    def turn_on_RF(self):
        """Abstract method for override that will turn on the RF device output.
    
        Args: 
    
        Returns:
            bool: Returns True if the output is enabled, False if it is not. 
        """
        pass

    @abstractmethod
    def turn_off_RF(self):
        """Abstract method for override that will turn off the RF device output.
    
        Args:
    
        Returns:
            bool: Returns True if the output is enabled, False if it is not.
        """
        pass

    @abstractmethod
    def get_output_state(self):
        """Abstract method for override that will get the current output state. 
    
        Args:
    
        Returns:
            bool: Returns True if the output is enabled, False if it is not. 
        """
        pass
