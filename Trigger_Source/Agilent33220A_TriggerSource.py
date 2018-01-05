from Generic_TriggerSource import *
import telnetlib
from pkg_resources import require

require("numpy")
import numpy as np
import warnings


class agilent33220a_wfmgen(Generic_TrigSource):
    """Rigol3030DSG RFSigGen, Child of Generic_RFSigGen.

    This class is for communicating with the Agilent33220A over telnet. The specific API calls abstract the SCPI 
    commands needed to speak with the instrument. Each of these calls is an override of the Generic_RFSigGen.

    Attributes:  
        *Inherited from parent.
    """

    # Private Methods
    def _telnet_query(self, message):
        """Private method that will send a message over telnet to the Rigol3030 and return the reply

        Args:
            message (str): SCPI message to be sent to the Agilent33220A

        Returns:
            str: Reply message from the Rigol3030
        """
        self._telnet_write(message)
        return self._telnet_read()

    def _telnet_write(self, message):
        """Private method that will send a message over telnet to the Agilent33220A

        Args:
            message (str): SCPI message to be sent to the Agilent33220A

        Returns:

        """
        # Checks that the telnet message is a string
        if type(message) != str:
            raise TypeError

        self.tn.write(message + "\r\n")  # Writes a telnet message with termination characters

    def _telnet_read(self):
        """Private method that will read a telnet reply from the Agilent33220A

        Args:

        Returns:
            str: Reply message from the Agilent33220A
        """
        return self.tn.read_until("\n", self.timeout).rstrip('\n')  # Telnet reply, with termination chars removed

    # Constructor and Deconstructor

    def __init__(self, ipaddress, port=5024, timeout=1):
        """Initialises and opens the connection to the Agilent33220A over telnet and informs the user 

        Args:
            ipaddress (str): The IP address of the Agilent33220A
            port (int/str): The port number for the messages to be sent on (default 5555)
            timeout (float): The timeout for telnet commands in seconds (default 1)

        Returns:

        """
        self.timeout = timeout  # timeout for the telnet comms
        self.tn = telnetlib.Telnet(ipaddress, port, self.timeout)  # connects to the telnet device
        self.get_device_ID()  # gets the device of the telnet device, makes sure its the right one
        self.turn_off_RF()  # turn off the RF output

        print("Opened connection to Trigger source" + self.DeviceID)  # tells the user the device has been connected to

    def __del__(self):
        """Closes the telnet connection to the Agilent33220A
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
        self.DeviceID = self._telnet_query("*IDN?")  # gets the device information
        test_string = "Welcome to Agilent's 33220A Waveform Generator"
        if self.DeviceID[0:len(test_string)] != test_string:  # checks it's the right device
            raise Exception("Wrong hardware device connected")
        return "Trigger Source " + self.DeviceID

    def set_up_trigger_pulse(self, freq):
        """Override method that will set up a pulse suitable for a trigger signal.

                Args:
                    freq (float)
                """
        self._telnet_write("FUNC:PULS:DCYC 50")
        self._telnet_write(''.join(("APPL:PULS ", str(freq), ', 1, 0')))
        self.turn_on_RF()

    def turn_on_RF(self):
        """Override method that will turn on the RF device output.

        Uses SCPI command "OUTP ON" to turn on the device.

        Args:

        Returns:
            bool: Returns True if the output is enabled, False if it is not. 
        """
        self._telnet_write("OUTP ON")  # turns on the output
        return self.get_output_state()

    def turn_off_RF(self):
        """Override method that will turn off the RF device output.

        Uses SCPI command "OUTP OFF" to turn off the device. 

        Args:

        Returns:
            bool: Returns True if the output is enabled, False if it is not.
        """
        self._telnet_write("OUTP OFF")  # turns off the output
        return self.get_output_state()

    def get_output_state(self):
        """Override method that will get the current output state. 

        This method send the SCPI command "OUTP?" to request the output state from
        the Rigol3030. 

        Args:

        Returns:
            bool: Returns True if the output is enabled, False if it is not. 
        """
        # checks output state
        if self._telnet_query("OUTP?") == "1":
            self.Output_State = True  # output must be on
            return True
        else:
            self.Output_State = False  # output must be off
            return False
