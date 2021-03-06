from Generic_RFSigGen import *
import common_device_functions.ITechBL12HI_common as itechbl12hi_common
from pkg_resources import require
require("numpy")
import numpy as np
import warnings


class ITechBL12HI_RFSigGen(Generic_RFSigGen):
    """ITechBL12HI RFSigGen, Child of Generic_RFSigGen.

    This class is for communicating with the ITechBL12HI over telnet. The specific API calls abstract the SCPI 
    commands needed to speak with the instrument. Each of these calls is an override of the Generic_RFSigGen.

    Attributes:  
        *Inherited from parent.
    """

    # Constructor and Deconstructor

    def __init__(self, ipaddress, port=5555, timeout=1, limit=-20):
        """Initialises and opens the connection to the ITechBL12HI over telnet and informs the user 

        Args:
            ipaddress (str): The IP address of the ITechBL12HI 
            port (int/str): The port number for the messages to be sent on (default 5555)
            timeout (float): The timeout for telnet commands in seconds (default 1)
            
        Returns:
            
        """
        self.timeout = timeout  # timeout for the telnet comms
        self.ipaddress = ipaddress
        self.port = port
        self.tn = itechbl12hi_common.telnet_setup(ipaddress, port, timeout)
        self.device_id = self.get_device_id()  # gets the device of the telnet device, makes sure its the right one
        self.turn_off_RF()  # turn off the RF output
        self.limit = limit  # set the RF output limit
        # self.set_output_power_limit(limit)  # set the RF output limit

        print("Opened connection to RF source " + self.device_id)  # tells the user the device has been connected to

    def __del__(self):
        """Closes the telnet connection to the ITechBL12HI
        """
        self.turn_off_RF()  # make sure the RF output is off
        self.tn.close()  # Closes the telnet connection
        print("Closed connection to RF source " + self.device_id)  # tell the user the telnet link has closed

    # API Calls
    def get_device_id(self):
        """Override method that will return the device ID."""
        return itechbl12hi_common.get_device_identity(self.tn,
                                                      timeout=self.timeout)

    def get_output_power(self):
        """Override method that will return the output power.
        
        Uses the "command POW:RF?"  to get the current output power level and units.
        
        Args:
        
        Returns:
            float: The current power value as a float in dBm
            str: The current output power concatenated with the units.
        """
        self.Output_Power = itechbl12hi_common.telnet_query(self.tn, self.timeout, "POW:RF?")
        return float(self._split_num_char(self.Output_Power)[0]), self.Output_Power

    def get_frequency(self):
        """Override method that will get the output frequency of the SigGen
        
        Uses the SCPI command "FREQ?" to get the set frequency. 
        
        Args:
        
        Returns:
            float: The current frequency value as a float and assumed units. 
            str: The current output frequency concatenated with the units.
        """

        self.Frequency, check = itechbl12hi_common.telnet_query(self.tn, self.timeout, "FREQ:RF?")  # get the device frequency
        return float(self.Frequency.replace(',', '.')[0:-4]), self.Frequency

    def set_frequency(self, frequency):
        """Override method that will set the output frequency.
        
        SCPI command "FREQ" is used to set the output frequency level. 
        
        Args:
            frequency (float): Desired value of the output frequency in MHz.
        Returns:
            float: The current frequency value as a float and assumed units. 
            str: The current output frequency concatenated with the units.
        """
        # check the input is a numeric
        if type(frequency) != float and type(frequency) != int \
                and np.float64 != np.dtype(frequency) and np.int64 != np.dtype(frequency):
            raise TypeError('Frequency value is not a float or int')
        # check the output is a positive number
        elif frequency < 0:
            raise ValueError('Frequency value is < 0')

        self.Frequency = frequency
        f_str = str(frequency).replace('.', ',')
        if len(f_str) == 6:
            # Adding the truncated 0
            f_str = f_str + '0'
        freq_str = ''.join(("FREQ:RF " + f_str))
        # Write the frequency value in MHz
        ret, check = itechbl12hi_common.telnet_query(self.tn, self.timeout, freq_str)
        return check

    def set_output_power(self, power):
        """Override method that will set the output power.
        
        The SCPI command "UNIT:POW" is used to set the units of the power output, then the 
        command "LEV" is used to set the output level in those units. 

        Args:
            power (float): Desired value of the output power in dBm.  
        Returns:
            float: The current power value as a float in dBm
            str: The current output power concatenated with the units. 
        """
        # check the input is a numeric
        if type(power) != float and type(power) != int \
                and np.float64 != np.dtype(power) and np.int64 != np.dtype(power):
            raise TypeError('Power value is not numeric')
        elif power > self.limit:  # If a value that is too high is used, the hardware may break.
            power = self.limit
            # tell the user the limit has been reached and cap the output level
            warnings.warn('Power limit has been reached, output will be capped')
        elif power < -50:
            power = -50
            warnings.warn('Power level is too low setting to -50 dBm')
        self.Output_Power = np.round(power)
        #  print 'Power = ', self.Output_Power
        # write the new output power
        ret, check = itechbl12hi_common.telnet_query(self.tn, self.timeout, "POW:RF " + str(self.Output_Power))
        return check

    def turn_on_RF(self):
        """Override method that will turn on the RF device output.
        
        Set the level to the requested power.
        This hardware does not have the ability to turn the RF source on and off."""
        itechbl12hi_common.turn_rf_on(self.tn,
                                      timeout=self.timeout,
                                      Output_Power=self.Output_Power)

    def turn_off_RF(self):
        """Override method that will turn off the RF device output.

        This device does not have the ability to turn off teh RF source.
        Instead it is turned down to the lowest level."""

        itechbl12hi_common.turn_rf_off(self.tn,
                                       timeout=self.timeout)

    def get_output_state(self):
        """Override method that will get the current output state. 
    
        This method send the SCPI command "POW:RF?" to request the output state from
        the ITechBL12HI. 
        
        Args:
        
        Returns:
            bool: Returns True if the output is enabled, False if it is not. 
        """
        pass

    def set_output_power_limit(self, limit):
        """Override method that will set a hardware limit for the output power

        Args:

        Returns:
            float: The power limit
        """
        # checks the input is a numeric
        if type(limit) != float and type(limit) != int \
                and np.float64 != np.dtype(limit) and np.int64 != np.dtype(limit):
            raise TypeError('Limit value is not numeric')
        self.limit = limit
        return self.get_output_power_limit()

    def get_output_power_limit(self):
        """Override method that will get the hardware limit for the output power
        
        Args:

        Returns:
            float: The power limit 
        """
        return self.limit, ''.join((str(self.limit), " dBm"))
