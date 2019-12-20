from ProgrammableAttenuator import *
import telnetlib
from pkg_resources import require
require("numpy")
import numpy as np
from time import sleep


class MC_RC4DAT6G95_Prog_Atten(Generic_Prog_Atten):

    def __init__(self, ipaddress, port, timeout):
        self.timeout = timeout  # timeout for the telnet comms
        #print ipaddress
        #print port
        self.tn = telnetlib.Telnet(ipaddress, port, self.timeout)  # connects to the telnet device
        # gets the device of the telnet device, makes sure its the right one
        self.DeviceID = self.get_device_id()
        print "Connected to Programmable attenuator" + self.DeviceID

    def __del__(self):
        self.tn.close()
        print "Closed connection to " + self.DeviceID

    def _telnet_query(self, message):
        """Private method that will send a message over telnet to the device

        Args:
            message (str): SCPI message to be sent to the device

        Returns:
            str: Reply message from the device
        """
        self._telnet_write(message)
        return self._telnet_read()

    def _telnet_write(self, message):
        """Private method that will send a message over telnet to the device

        Args:
            message (str): SCPI message to be sent to the device

        Returns:

        """
        # Checks that the telnet message is a string
        if type(message) != str:
            raise TypeError

        self.tn.write(message + "\r\n")  # Writes a telnet message with termination characters

    def _telnet_read(self):
        """Private method that will read a telnet reply from the device

        Args:

        Returns:
            str: Reply message from the device
        """
        prev_status = self.tn.read_until("\r\n", self.timeout)
        ret_val = self.tn.read_until("\r\n", self.timeout)
        # Sometimes the device adds an additional carriage return.
        if ret_val:
            string_total = ret_val.replace('\r\n', "")  # Telnet reply, with termination chars removed
        else:
            string_total = prev_status.replace('\r\n', "")  # Telnet reply, with termination chars removed
        #print 'Return string = ', string_total
        return string_total

    def _check_attenuation(self, attenuation):
        if type(attenuation) != float and type(attenuation) != int \
                and np.float64 != np.dtype(attenuation) and np.int64 != np.dtype(attenuation):
            raise TypeError
        if attenuation > 95 or attenuation < 0:
            raise ValueError

    def _check_channel(self, channel):
        if type(channel) == int:
            while channel not in [1, 2, 3, 4]:
                raise ValueError
        else:
            raise TypeError

    def get_device_id(self):
        model = self._telnet_query("MN?")  # gets the device information
        model = model.replace("MN=", "")
        if "RC4DAT-6G-95" not in model:
            print 'Returned string ', model
            raise ValueError("Wrong device connected")
        return model

    def set_global_attenuation(self, attenuation):
        if type(attenuation) != float and type(attenuation) != int \
                and np.float64 != np.dtype(attenuation) and np.int64 != np.dtype(attenuation):
            raise TypeError
        if attenuation > 95 or attenuation < 0:
            print 'Odd attenuation value ', attenuation
            raise ValueError
        self._check_attenuation(attenuation)
        self._telnet_query(":CHAN:1:2:3:4:SETATT:" + str(attenuation))
        # print 'Attenuation requested', attenuation, 'Attenuation set', self.get_global_attenuation()

    def get_global_attenuation(self):
        replies = self._telnet_query(':ATT?')
        replies = replies.split()
        replies = map(float, replies)
        return replies

    def set_channel_attenuation(self, channel, attenuation):
        """

                Args:
                    channel (int): The channel of the attenuator to use. This is in native values of 1,2,3,4.
                    attenuation (float): The value of attenuation to use. Possible values 0-95 in steps of 0.25.

                Returns:
                     float: Value of the attenuator on that channel.
                """
        self._check_attenuation(attenuation)
        self._check_channel(channel)
        if type(channel) == str:
            raise TypeError
        command = ":CHAN:" + str(channel) + ":SETATT:" + str(attenuation)
        self._telnet_write(command)
        test = self.get_channel_attenuation(channel)
        if attenuation != test:
            self._telnet_write(command)
            test = self.get_channel_attenuation(channel)
        # print 'Channel ', channel, ' Attenuation requested', attenuation, 'Attenuation set', test

    def get_channel_attenuation(self, atten_channel):
        """
        
        Args:
             atten_channel (number): The channel of the attenuator to use. This is in native values of 1,2,3,4.
        
        Returns:
             float: Value of the attenuator on that channel.
        """
        self._check_channel(atten_channel)
        if type(atten_channel) == str:
            raise TypeError
        else:
            command = ":ATT?"
        reply = self._telnet_query(':ATT?')
        for md in range(10):
            if not reply:  # Checking for an empty string.
                print 'Got nothing back .... Trying again.'
                reply = self._telnet_query(command)
                sleep(0.5)
            else:
                if md > 0:
                    print 'Get Channel reply = ', reply
                break
            if md == 9:
                raise IOError
        vals = reply.split()
        return float(vals[atten_channel - 1])
