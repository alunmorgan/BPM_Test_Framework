from Generic_TriggerSource import *
import telnetlib
import re
from pkg_resources import require

require("numpy")
import numpy as np
import warnings


class ITechBL12HI_trigsrc(Generic_TrigSource):
    """Rigol3030DSG RFSigGen, Child of Generic_RFSigGen.

    This class is for communicating with the ITechBL12HI over telnet. The specific API calls abstract the SCPI 
    commands needed to speak with the instrument. Each of these calls is an override of the Generic_RFSigGen.

    Attributes:  
        *Inherited from parent.
    """

    # Private Methods
    def _telnet_query(self, message):
        """Private method that will send a message over telnet to the ITechBL12HI and return the reply
            This needs to open and close a connection in order to isolate the replies. If one connection is opened on
            this hardware the responses do not block so several responses can arrive before the first read.
            So the wrong data is read.

        Args:
            message (str): SCPI message to be sent to the ITechBL12HI

        Returns:
            str: Reply message from the ITechBL12HI
        """
        # Checks that the telnet message is a string
        if type(message) != str:
            raise TypeError
        self.tn = telnetlib.Telnet(self.ipaddress, self.port, self.timeout)  # Connects to the IP via telnet
        self.tn.read_until("\n", self.timeout).rstrip('\n')
        self.tn.read_until("\n", self.timeout).rstrip('\n')
        self.tn.write("scpi>\r\n")  # putting the device into scpi mode.
        self.tn.write(message + "\r\n")  # Writes a telnet message with termination characters
        r_str = self.tn.read_until("\n", self.timeout).rstrip('\n')  # Telnet reply, with termination chars removed
        message_pattern = re.compile('(?:scpi>)*\S*\s+(.*)')
        message = re.match(message_pattern, r_str)
        # Status line. Needs to be read to make the following read be at the correct place
        check = self.tn.read_until("\n", self.timeout).rstrip('\n')  # Status line
        self.tn.close()  # Closes the telnet connection
        if 'OK' not in check:
            print 'Bad status  STATUS = ', check, type(check)
            print 'Sent command = ', r_str
            print 'Return = ', message.group(1)
        return message.group(1), check

    def _telnet_write(self, message):
        """Private method that will send a message over telnet to the ITechBL12HI

        Args:
            message (str): SCPI message to be sent to the ITechBL12HI

        Returns:

        """
        pass

    def _telnet_read(self):
        """Private method that will read a telnet reply from the ITechBL12HI
            NOT USED ON THIS HARDWARE.
        Args:

        Returns:
            str: Reply message from the ITechBL12HI
        """
        pass

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
        self.get_device_ID()  # gets the device of the telnet device, makes sure its the right one
        self.turn_off_RF()  # turn off the RF output

        print("Opened connection to Trigger source" + self.DeviceID)  # tells the user the device has been connected to

    def __del__(self):
        """Closes the telnet connection to the ITechBL12HI
        """
        self.turn_off_RF()  # make sure the RF output is off
        self.tn.close()  # close the telnet link
        print("Closed connection to " + self.DeviceID)  # tell the user the telnet link has closed

    # API Calls
    def get_device_ID(self):
        """Override method that will return the device ID.

        Uses the SCPI command "*IDN?" to get the device ID.

        Args:

        Returns:
            str: The DeviceID of the SigGen.
        """
        # print 'Getting Device ID'
        self.DeviceID, check = self._telnet_query("*IDN?\r\n")  # gets the device information
        if "IT CLKGEN" not in self.DeviceID:  # checks it's the right device
            print "ID= ", self.DeviceID
            raise Exception("Wrong hardware device connected")
        return "RF Source " + self.DeviceID

    def set_up_trigger_pulse(self, freq):
        """Override method that will set up a trigger signal.

                Args:
                    freq (float)
                """
        pass

    def turn_on_RF(self):
        """Override method that will turn on the RF device output.

        Set the level to the requested power. This hardware does not have the ability to turn the RF source on and off.

        Args:

        Returns:
            bool: Returns True if the output is enabled, False if it is not.
        """
        ret, check = self._telnet_query("POW:RF " + self.Output_Power)  # turns on the output
        if check == 'OK':
            self.Output_State = True
        else:
            self.Output_State = False
        return self.Output_State

    def turn_off_RF(self):
        """Override method that will turn off the RF device output.

        This device does not have the ability to turn off teh RF source.
        Instead it is turned down to the lowest level.

        Args:

        Returns:
            bool: Returns True if the output is enabled, False if it is not.
        """
        ret, check = self._telnet_query("POW:RF -50")  # turns off the output
        if check == 'OK':
            self.Output_State = False
        else:
            self.Output_State = True
        return self.Output_State

    def get_output_state(self):
        """Override method that will get the current output state.

        This method send the SCPI command "POW:RF?" to request the output state from
        the ITechBL12HI.

        Args:

        Returns:
            bool: Returns True if the output is enabled, False if it is not.
        """
        # checks output state
        ret, check = self._telnet_query("POW:RF?")
        if "-50" in ret:
            self.Output_State = False  # output must be off
            return False
        else:
            self.Output_State = True  # output must be on
            return True
