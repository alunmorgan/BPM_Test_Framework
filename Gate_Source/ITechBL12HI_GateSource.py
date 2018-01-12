from Generic_GateSource import *
import telnetlib
import re
from pkg_resources import require
require("numpy")
import numpy as np


class CustomException(Exception):
    pass


class ITechBL12HI_GateSource(Generic_GateSource):

    # Private Methods
    def _telnet_query(self, message):
        """Private method that will send a message over telnet to the ITechBL12HI and return the reply.
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
        print 'Sent command = ', r_str
        print 'Return = ', message.group(1)
        print 'Status = ', check
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

    def __init__(self, ipaddress, port=5555, timeout=1):
        """Initialises and opens the connection to the ITechBL12HI over telnet and informs the user 

        Args:
            ipaddress (str): The IP address of the ITechBL12HI
            port (int/str): The port number for the messages to be sent on (default 5555)
            timeout (float): The timeout for telnet commands in seconds (default 1)
            
        Returns:
            
        """
        self.timeout = timeout  # Sets timeout for the telnet calls
        self.ipaddress = ipaddress
        self.port = port
        self.get_device_ID()  # Gets the device ID, checks connection is made
        self.modulation_state = False  # Default parameter for the modulation state
        #self.turn_off_modulation()  # Turns off the signal modulation
        #self.pulse_period = self.get_pulse_period()  # Not setable on this hardware.
        self.set_pulse_dutycycle(0)  # Sets the duty cycle to 0 by default
        print("Opened connection to gate source " + self.DeviceID)  # Inform the user the device is connected to

    def __del__(self):
        """Closes the telnet connection to the ITechBL12HI
        
        Args:
            
        Returns:
        
        """
        self.turn_off_modulation()  # Turns off the signal modulation
        self.tn.close()  # Closes the telnet connection
        print("Closed connection to gate source " + self.DeviceID)  # Lets the user know connection is closed

    # API Methods
    def get_device_ID(self):
        """Override method that will return the device ID.

        Uses the SCPI command "*IDN?" to get the device ID.

        Args:

        Returns:
            str: The DeviceID of the SigGen.
        """
        self.DeviceID, check = self._telnet_query("*IDN?\r\n")  # gets the device information
        if "IT CLKGEN" not in self.DeviceID:  # checks it's the right device
            print "ID= ", self.DeviceID
            raise Exception("Wrong hardware device connected")
        return "RF Source " + self.DeviceID

    def turn_on_modulation(self):
        """Override method, Turns on the pulse modulation.

        This will modulate the RF output.
        The RF output must turned off/on independently.

        Args: 
            
        Returns:

        """
        ret, check = self._telnet_query("GATE:FILL 0")  # Turns on the modulation state output
        if check == 'OK':
            self.modulation_state = True
        else:
            self.modulation_state = False
        return self.modulation_state

    def turn_off_modulation(self):
        """Override method, Turns on the pulse modulation.

        This function will turn off the modulation of the RF output 
        The RF output must turned off/on independently.

        Args: 

        Returns:

        """
        ret, check = self._telnet_query("GATE:FILL 100")  # Turns off the modulation state output
        if check == 'OK':
            self.modulation_state = False
        else:
            self.modulation_state = True
        return self.modulation_state

    def get_modulation_state(self):
        """Override method, Checks if the pulse modulation is on or off

        Args: 

        Returns:

        """
        modulation, check = self._telnet_query("GATE:FILL?")  # Checks the modulation state
        if modulation == "100 %":
            self.modulation_state = False  # If it isn't, return a False
        elif modulation != "100 %":
            self.modulation_state = True  # If it is, return a True
        return self.modulation_state

    def get_pulse_period(self):
        """Override method, Gets the total pulse period of the modulation signal

        Args: 

        Returns:
            float: The pulse period in float form
            str: The units that the pulse period is measured in 

        """
        m_clk, check = self._telnet_query("FREQ:MC?")
        m_num = m_clk[0:-4]
        m_num2 = float(m_num.replace(',', '.'))  # MHz
        self.pulse_period = 1. / m_num2  # Gets the pulse period of the device
        # Returns the pulse period as a float, and a string with the units
        return self.pulse_period, "us"

    def set_pulse_period(self, period):
        """Override method, Sets the total pulse period of the modulation signal
            THIS IS UNUSED FOR THIS HARDWARE!
        Args:
            period (float): The period of the pulse modulation signal is uS.

        Returns:
            float: The pulse period in float form.
        """
        ret, check = self._telnet_query("FREQ:MC " + str(1. / period))
        return check

    def get_pulse_dutycycle(self):
        """Override method, Gets the duty cycle of the modulation signal

        The duty cycle of the signal will be set as a decimal of the pulse period.
        If the pulse period is 100us and the duty cycle input is 0.3, the pulse that 
        modulates the RF will be on for 30us, then off for 70us, then repeat. This 
        will return the decimal value.

         Args: 

         Returns:
             float: decimal value (0-1) of the duty cycle of the pulse modulation
         """
        fill, check = self._telnet_query("GATE:FILL?")  # calculates the duty cycle and returns it
        g_fill = float(fill[0:-2])
        return g_fill / 100.

    def set_pulse_dutycycle(self, dutycycle):
        """Override method, Gets the duty cycle of the modulation signal

        The duty cycle of the signal will be set as a decimal (0 - 1). This
        will return the decimal value.

        Args: 
            dutycycle (float): decimal value of the duty cycle (0-1) for the pulse modulation
        Returns:
            float: decimal value (0-1) of the duty cycle of the pulse modulation 
        """
        # makes sure the duty cycle value is a numeric
        if type(dutycycle) != float and type(dutycycle) != int and np.float64 != np.dtype(dutycycle):
            raise TypeError
        # makes sure the duty cycle value is a decimal between 0 and 1
        elif dutycycle > 1 or dutycycle < 0:
            raise ValueError
        duty_str = "GATE:FILL " + str(dutycycle * 100) + '\r\n'
        ret, check = self._telnet_query(duty_str)  # writes the calculated pulse width
        return check

    def invert_pulse_polarity(self, polarity):
        """Inverts the polarity of the gate signal
            THIS IS UNUSED FOR THIS HARDWARE!
        True will invert the signal, false will return it to it's default state.

        Args:
            polarity (bool): boolean that decides the inversion state
        Returns:
            bool: The current state of the inversion
        """

        return self.get_pulse_polarity()

    def get_pulse_polarity(self):
        """Checks if the signal is inverted or not

        Args:
        Returns:
            bool: The current state of the inversion
        """
        return True
