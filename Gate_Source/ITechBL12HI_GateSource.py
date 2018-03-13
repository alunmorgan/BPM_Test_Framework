from Generic_GateSource import *
import common_device_functions.ITechBL12HI_common as itechbl12hi_common
from pkg_resources import require
require("numpy")
import numpy as np


class CustomException(Exception):
    pass


class ITechBL12HI_GateSource(Generic_GateSource):
    # Constructor and Deconstructor

    def __init__(self, tn, timeout):
        """Initialises and opens the connection to the ITechBL12HI over telnet and informs the user 

        Args:
            tn (Obj): telnet object for the device
            timeout (float): The timeout for telnet commands in seconds (default 1)
            
        Returns:
            
        """
        self.timeout = timeout  # Sets timeout for the telnet calls
        self.tn = tn
        self.device_id = self.get_device_id()  # Gets the device ID, checks connection is made
        self.modulation_state = self.get_modulation_state()
        self.set_pulse_dutycycle(0)  # Sets the duty cycle to 0 by default
        print("Opened connection to gate source " + self.device_id)  # Inform the user the device is connected to

    def __del__(self):
        """Closes the telnet connection to the ITechBL12HI
        
        Args:
            
        Returns:
        
        """
        self.turn_off_modulation()  # Turns off the signal modulation
        # Lets the user know connection is closed
        print("Closed connection to gate source " + self.device_id)

    # API Methods
    def get_device_id(self):
        #     """Override method that will return the device ID.
        return itechbl12hi_common.get_device_identity(self.tn,
                                                      timeout=self.timeout)

    def turn_on_modulation(self):
        """Override method, Turns on the pulse modulation.

        This will modulate the RF output.
        The RF output must turned off/on independently.

        Args: 
            
        Returns:

        """
        ret, check = itechbl12hi_common.telnet_query(self.tn, self.timeout, "GATE:FILL 0")  # Turns on the modulation state output
        if 'OK' in check:
            self.modulation_state = True
        else:
            self.modulation_state = None
            raise IOError("Gate modulation in unknown state")

        return self.modulation_state

    def turn_off_modulation(self):
        """Override method, Turns on the pulse modulation.

        This function will turn off the modulation of the RF output 
        The RF output must turned off/on independently.

        Args: 

        Returns:

        """
        ret, check = itechbl12hi_common.telnet_query(self.tn, self.timeout, "GATE:FILL 100")  # Turns off the modulation state output
        if 'OK' in check:
            self.modulation_state = False
        else:
            self.modulation_state = None
            raise IOError("Gate modulation in unknown state")

        return self.modulation_state

    def get_modulation_state(self):
        """Override method, Checks if the pulse modulation is on or off

        Args: 

        Returns:

        """
        modulation, check = itechbl12hi_common.telnet_query(self.tn, self.timeout, "GATE:FILL?")  # Checks the modulation state
        if modulation == "100 %":
            modulation_state = False  # If it isn't, return a False
        else:
            modulation_state = True  # If it is, return a True
        return modulation_state

    def get_pulse_period(self):
        """Override method, Gets the total pulse period of the modulation signal

        Args: 

        Returns:
            float: The pulse period in float form
            str: The units that the pulse period is measured in 

        """
        m_clk, check = itechbl12hi_common.telnet_query(self.tn, self.timeout, "FREQ:MC?")
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
            check(str): The status of the command.
        """
        # if type(period) != float and type(period) != int \
        #         and np.float64 != np.dtype(period) and np.int64 != np.dtype(period):
        #     raise TypeError
        #
        # if period < 0:
        #     raise ValueError("Pulse period must have a positive value.")
        #
        # command = "FREQ:MC " + str(1. / period) # IN Hz or MHz?
        # command = command.replace('.', ',')
        # print command
        # ret, check = common.telnet_query(self.ipaddress, self.port, self.timeout, "DEV:MODE RF")
        # ret, check = common.telnet_query(self.ipaddress, self.port, self.timeout, command)
        return True

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
        fill, check = itechbl12hi_common.telnet_query(self.tn, self.timeout, "GATE:FILL?")  # calculates the duty cycle and returns it
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
            raise TypeError('Duty cycle is not numeric')
        # makes sure the duty cycle value is a decimal between 0 and 1
        elif dutycycle > 1 or dutycycle < 0:
            raise ValueError('Duty cycle is >1 or < 0')
        duty_str = "GATE:FILL " + str(int(np.round(dutycycle * 100))) + '\r\n'
        # writes the calculated pulse width
        ret, check = itechbl12hi_common.telnet_query(self.tn, self.timeout, duty_str)
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
