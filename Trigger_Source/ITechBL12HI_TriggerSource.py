from Generic_TriggerSource import *
import common_device_functions.ITechBL12HI_common as common
from pkg_resources import require
require("numpy")
import numpy as np
import warnings


class ITechBL12HI_trigsrc(Generic_TrigSource):
    """ITechBL12HI RFSigGen, Child of Generic_RFSigGen.

    This class is for communicating with the ITechBL12HI over telnet. The specific API calls abstract the SCPI 
    commands needed to speak with the instrument. Each of these calls is an override of the Generic_RFSigGen.

    Attributes:  
        *Inherited from parent.
    """
    # Constructor and Deconstructor

    def __init__(self, ipaddress, port=5024, timeout=1):
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
        self.DeviceID = self.get_device_id()  # gets the device of the telnet device, makes sure its the right one
        self.turn_off_RF()  # turn off the RF output

        print("Opened connection to Trigger source" + self.DeviceID)  # tells the user the device has been connected to

    def __del__(self):
        """Closes the telnet connection to the ITechBL12HI
        """
        self.turn_off_RF()  # make sure the RF output is off
        # self.tn.close()  # close the telnet link
        print("Closed connection to " + self.DeviceID)  # tell the user the telnet link has closed

    # API Calls
    def get_device_id(self):
        """Override method that will return the device ID."""
        return common.get_device_identity(ipaddress=self.ipaddress,
                                          port=self.port,
                                          timeout=self.timeout)

    def set_up_trigger_pulse(self, freq):
        """Override method that will set up a trigger signal.

                Args:
                    freq (float)
                """
        pass

    def turn_on_RF(self):
        """Override method that will turn on the RF device output.

        Set the level to the requested power.
        This hardware does not have the ability to turn the RF source on and off."""
        common.turn_rf_on(ipaddress=self.ipaddress,
                          port=self.port,
                          timeout=self.timeout,
                          Output_Power=self.Output_Power)

    def turn_off_RF(self):
        """Override method that will turn off the RF device output.

        This device does not have the ability to turn off teh RF source.
        Instead it is turned down to the lowest level."""

        common.turn_rf_off(ipaddress=self.ipaddress,
                           port=self.port,
                           timeout=self.timeout)

    def get_output_state(self):
        """Override method that will get the current output state.

        This method send the SCPI command "POW:RF?" to request the output state from
        the ITechBL12HI.

        Args:

        Returns:
            bool: Returns True if the output is enabled, False if it is not.
        """
        # checks output state
        ret, check = common.telnet_query(self.ipaddress, self.port, self.timeout, "POW:RF?")
        if "-50" in ret:
            self.Output_State = False  # output must be off
            return False
        else:
            self.Output_State = True  # output must be on
            return True
