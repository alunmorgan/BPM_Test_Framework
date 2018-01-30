import telnetlib
from Generic_BPMDevice import *
from subprocess import Popen, PIPE
from pkg_resources import require
require("numpy")
import numpy as np


class SparkER_SCPI_BPMDevice(Generic_BPMDevice):
    """BPM Device class that uses SCPI commands to communicate with Libera SparkER

    All of the Spark ER commands listed here can be written to the device using Telnet,
    to find the full list of commands please find the Spark ER documentation. Mainly
    raw ADC values where the RMS is extracted, and TBT data that is then averaged.
    This class is for use in her BPM testing framework. 

    Attributes:
        IP Address (str): IP address of the device
        Port (int): Port to communicate to the device on 
        Timeout (float): Timeout to wait for a response 
    """

    def _telnet_query(self, message, timeout=1.0):
        """Private method that will send a message over telnet to the SparkER and return the reply

        Args:
            message (str): SCPI message to be sent to the SparkER
        Returns:
            str: Reply message from the SparkER
        """
        self._telnet_write(message)
        return self._telnet_read()

    def _telnet_write(self, message):
        """Private method that will send a message over telnet to the SparkER
        
        If the device does not have an external trigger, it will be software
        triggered if the autoTrig is set. 

        Args:
            message (str): SCPI message to be sent to the SparkER
        Returns:
        """
        self.tn.write(message + "\r\n") # Writes to the telnet device, adds termination characters

    def _telnet_read(self, timeout=1.0):
        """Private method that will read a telnet reply from the SparkER

        Args:
        Returns:
            str: Reply message from the SparkER
        """
        return self.tn.read_until('\r\n',timeout).rstrip('\n') # Gets the reply, removes termination characters

    def _get_mac_address(self):
        node = self.IP  # Get the devices IP address
        host_info = Popen(["arp", "-n", node], stdout=PIPE).communicate()[0]  # arp with the device
        host_info = host_info.split("\n")[1]  # split the information the host gives
        index = host_info.find(":")  # find the index of the first ":" (used in the MAC address)
        host_info = host_info[index - 2:index + 15]  # Return the MAC address
        return host_info

    def _trigger_DAQ(self):
        """Private method to fire a software trigger to update the DAQ

        This will write a "TRIG" record that will update all of the 
        process variables on that database. 

        Args: 

        Returns: 
        """
        if self.autoTrig == 1: # If the hardware has no trigger connected, use a software trigger
            self._telnet_query("TRIG") # Fires a software trigger to the hardware to update the values
        else:
            pass

    def __init__(self, IPaddress, port, timeout, autoTrig = 1):
        """Initializes the Libera BPM device object and assigns it an ID. 

        Args:
            dev_ID (str/int): The two digit ID number assigned to that specific BPM device. 
        Returns:
.
        """
        self.autoTrig = autoTrig
        self.IP = IPaddress
        self.timeout = timeout
        self.tn = telnetlib.Telnet(IPaddress, port, self.timeout) # Opens telnet connection
        self.mac_address = self._get_mac_address()
        self.DeviceID = self.get_device_id()
        self._telnet_query("START") # starts the device
        self._trigger_DAQ()
        print("Opened connection to " + self.DeviceID)  # Informs the user the device is connected

    def __del__(self):
        self.tn.close()  # Disconnects telnet device
        print("Closed connection to " + self.DeviceID)  # Informs the user the device is disconnected

    def get_x_position(self):
        """Override method, gets the calculated X position of the beam.

        Args:

        Returns: 
            float: X position in mm
        """
        self._trigger_DAQ()
        replies = self._telnet_query("TBT_XY 100")  # Get 100 samples of XY data
        replies = replies.rsplit()  # Split the data into lists
        replies = np.array(map(float, replies))  # Convert the data into a float array
        x = replies[0::2]  # Grab the X data only
        mean_x = np.mean(x)  # Calculate the average of the X data
        mean_x = mean_x / 1000  # convert um to mm
        return mean_x

    def get_y_position(self):
        """Override method, gets the calculated Y position of the beam.

        Args:

        Returns: 
            float: Y position in mm
        """
        self._trigger_DAQ()
        replies = self._telnet_query("TBT_XY 100")  # Get 100 samples of XY data
        replies = replies.rsplit()  # Split the data into lists
        replies = np.array(map(float, replies))  # Convert the data into a float array
        y = replies[1::2]  # Grab the Y data only
        mean_y = np.mean(y)  # Calculate the average of the Y data
        mean_y = mean_y / 1000  # convert um to mm
        return mean_y

    def get_x_sa_data(self, num_vals):
        """Override method, gets the calculated X position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), X position in mm]
        """
        self._trigger_DAQ()
        replies = self._telnet_query(" ".join(("TBT_XY", num_vals)))  # Get 100 samples of XY data
        replies = replies.rsplit()  # Split the data into lists
        replies = np.array(map(float, replies))  # Convert the data into a float array
        sa_x_data = replies[0::2]  # Grab the X data only
        return sa_x_times, sa_x_data  #WHAT ABOUT THE TIMESTAMPS

    def get_y_sa_data(self, num_vals):
        """Override method, gets the calculated X position SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns: 
            list: [raw_timestamp (tuple), X position in mm]
        """
        self._trigger_DAQ()
        replies = self._telnet_query(" ".join(("TBT_XY", num_vals)))  # Get 100 samples of XY data
        replies = replies.rsplit()  # Split the data into lists
        replies = np.array(map(float, replies))  # Convert the data into a float array
        sa_y_data = replies[1::2]  # Grab the Y data only
        return sa_y_times, sa_y_data  #WHAT ABOUT THE TIMESTAMPS

    def get_sa_data(self, num_vals):
        """Gets the ABCD SA data.

        Args:
            num_vals (int): The number of samples to capture
        Returns:
            timestamps (list): floats
            data (list): floats
        """

        sa_a_times = None
        sa_a_data = None
        sa_b_times = None
        sa_b_data = None
        sa_c_times = None
        sa_c_data = None
        sa_d_times = None
        sa_d_data = None

        return sa_a_times, sa_a_data, sa_b_times, sa_b_data, sa_c_times, sa_c_data, sa_d_times, sa_d_data

    def get_tt_data(self):
        """ Gets the calculated ABCD TT data.

        Args:
            num_vals (int): The number of samples to capture
       Returns:
            times (list): floats
            data (list): floats
        """
        times = None
        data1 = None
        data2 = None
        data3 = None
        data4 = None

        return times, data1, data2, data3, data4

    def get_adc_data(self):
        """ Gets the ABCD ADC data.

        Args:
            num_vals (int): The number of samples to capture
        Returns:
            timestamps (list): floats
            adc1_data (list): floats
            adc2_data (list): floats
            adc3_data (list): floats
            adc4_data (list): floats
        """
        times = None
        adc1_data = None
        adc2_data = None
        adc3_data = None
        adc4_data = None

        return times, adc1_data, adc2_data, adc3_data, adc4_data

    def get_ft_data(self):
        """ Gets the ABCD first turn data.

        Args:
            num_vals (int): The number of samples to capture
       Returns:
            timestamps (list): floats
            data (list): floats
        """
        times = None
        fta_data = None
        ftb_data = None
        ftc_data = None
        ftd_data = None

        return times, fta_data, ftb_data, ftc_data, ftd_data

    def get_beam_current(self):
        """Override method, gets the beam current read by the BPMs. 

        Args:

        Returns: 
            float: Current in mA
        """
        self._trigger_DAQ()
        # This is not finished, only records ADC counts, not in mA
        replies = self._telnet_query("TBT_QSUM 100")
        replies = replies.rsplit()
        replies = np.array(map(float, replies))
        q = replies[0::2]
        bpm_sum = replies[1::2]
        mean_q = np.mean(q)
        mean_sum = np.mean(bpm_sum)
        return mean_sum

    def get_input_power(self):
        """Override method, gets the input power of the signals input to the device 

        Args:

        Returns: 
            float: Input power in dBm
        """
        # This is not finished, only records ADC counts, not in dBm
        self._trigger_DAQ()
        replies = self._telnet_query("TBT_QSUM 100")
        replies = replies.rsplit()
        replies = np.array(map(float, replies))
        q = replies[0::2]
        bpm_sum = replies[1::2]
        mean_q = np.mean(q)
        mean_sum = np.mean(bpm_sum)
        return mean_sum

    def get_raw_bpm_buttons(self):
        """Override method, gets the raw signal from each BPM.

        Args: 

        Returns: 
            float: Raw signal from BPM A
            float: Raw signal from BPM B
            float: Raw signal from BPM C
            float: Raw signal from BPM D
        """
        self._trigger_DAQ()
        replies = self._telnet_query("ADC 200")  # Get 200 samples of ADC data
        replies = replies.rsplit()  # Convert the string in to a list of values
        replies = np.array(map(float, replies))  # Convert these into a flaot array
        a = replies[0::4]  # Get the A button data only
        b = replies[1::4]  # Get the B button data only
        c = replies[2::4]  # Get the C button data only
        d = replies[3::4]  # Get the D button data only
        rms_a = np.sqrt(np.mean(np.square(a)))  # Get the RMS value
        rms_b = np.sqrt(np.mean(np.square(b)))  # Get the RMS value
        rms_c = np.sqrt(np.mean(np.square(c)))  # Get the RMS value
        rms_d = np.sqrt(np.mean(np.square(d)))  # Get the RMS value
        return rms_a, rms_b, rms_c, rms_d

    def get_normalised_bpm_buttons(self):
        """Override method, gets the normalised signal from each BPM.

        Args: 

        Returns: 
            float: Normalised signal from BPM A
            float: Normalised signal from BPM B
            float: Normalised signal from BPM C
            float: Normalised signal from BPM D
        """
        a, b, c, d = self.get_raw_bpm_buttons()  # Get the RAW ADC button values
        sum = a + b + c + d  # Get the sum of these values
        sum = sum/4  # Get the average BPM value
        a = a/sum  # Normalise the BPM value
        b = b/sum  # Normalise the BPM value
        c = c/sum  # Normalise the BPM value
        d = d/sum  # Normalise the BPM value
        return a, b, c, d

    def get_device_id(self):
        """Override method, gets the device's epics ID and MAC address 

        Args:

        Returns: 
            str: Device with epics channel ID and MAC address
        """

        return "Spark BPM \"" + self.mac_address + "\""

    def get_adc_sum(self):
        """Override method, gets the maximum input power the device can take

        The devices will break if the input power is too high, as such, each device has their
        own tolerances, this function will return this tolerance. It should be used to ensure 
        that the power put into the device is not too high to break the device. 

        Args:
        Returns: 
            int: sum of the ADC buttons
        """
        self._trigger_DAQ()
        # This is not finished, only records ADC counts, not in mA
        replies = self._telnet_query("TBT_QSUM 100")  # Grab 100 samples of Q sum data
        replies = replies.rsplit()  # Split the values into a list
        replies = np.array(map(float, replies))  # Convert the list into a float array
        q = replies[0::2]  # Grab the Q data only
        bpm_sum = replies[1::2]  #  Grab the Sum data only
        mean_q = np.mean(q)  # Calculate the mean Q value
        mean_sum = np.mean(bpm_sum)  # Calculate the mean Sum value
        mean_sum = np.round(mean_sum)  # round the Sum to an integer
        return mean_sum  # return the mean sum

    def get_input_tolerance(self):
        """Override method, gets the maximum input power the device can take

        The devices will break if the input power is too high, as such, each device has their
        own tolerances, this function will return this tolerance. It should be used to ensure 
        that the power put into the device is not too high to break the device. 

        Args:

        Returns: 
            float: max input power in dBm
        """
        return -40  # The maximum continuous input power the spark can handle in dBm

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
        specs = {}
        specs['noise_10kHz'] = ([0, -24, -32, -40, -44, -50, -56, -62, -68, -74, -80],
                                [0.2, 0.3, 0.5, 1, 2, 4, 5, 10, 20, 50, 100])
        specs['noise_1MHz'] = ([0, -32, -36, -40, -44, -50, -56, -62, -68, -74, -80],
                               [3, 5, 6, 8, 15, 30, 50, 150, 300, 600, 1500])
        specs['Beam_current_dependence_X'] = ([0, -2, -56, -68, -74, -80],
                                              [0, 1, 2, 10, 20, 50])
        specs['Beam_current_dependence_Y'] = ([0, -2, -56, -68, -74, -80],
                                              [0, 1, 2, 10, 20, 50])
        specs['Beam_current_dependence_deviation_within_range_X'] = \
            ([[0, -8], [-8, -20], [-20, -32], [-32, -40], [-40, -56], [-56, -68], [-68, -70]],
             [1, 1, 1, 1, 1, 5, 50])
        specs['Beam_current_dependence_deviation_within_range_Y'] = \
            ([[0, -8], [-8, -20], [-20, -32], [-32, -40], [-40, -56], [-56, -68], [-68, -70]],
             [1, 1, 1, 1, 1, 5, 50])

        specs['Fill_pattern_dependence_X'] = ([20, 100], 1)
        specs['Fill_pattern_dependence_Y'] = ([20, 100], 1)

        return specs
