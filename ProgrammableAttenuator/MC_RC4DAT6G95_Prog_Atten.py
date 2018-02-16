from ProgrammableAttenuator import *
import telnetlib
from pkg_resources import require
require("numpy")
import numpy as np
from time import sleep


class MC_RC4DAT6G95_Prog_Atten(Generic_Prog_Atten):

    def __init__(self, ipaddress, port, timeout):
        self.timeout = timeout  # timeout for the telnet comms
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
        string_1 = self.tn.read_until("\r\n", self.timeout)
        string_2 = self.tn.read_until("\r\n", self.timeout)
        string_total = string_1+string_2
        string_total = string_total.replace('\r\n', "")  # Telnet reply, with termination chars removed
        return string_total

    def _check_attenuation(self, attenuation):
        if type(attenuation) != float and type(attenuation) != int \
                and np.float64 != np.dtype(attenuation) and np.int64 != np.dtype(attenuation):
            raise TypeError
        if attenuation > 95 or attenuation < 0:
            raise ValueError

    def _check_channel(self, channel):
        if type(channel) == str:
            channel = channel.upper()
            while channel not in ["A", "B", "C", "D"]:
                raise ValueError
        elif type(channel) == int:
            while channel not in [1, 2, 3, 4]:
                raise ValueError
        else:
            raise TypeError

    def get_device_id(self):
        model = self._telnet_query("MN?")  # gets the device information
        model = model.replace("MN=", "")
        if model != "RC4DAT-6G-95":
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
        self._telnet_query(":CHAN:1:2:3:4:SetAtt:"+str(attenuation))
        return self.get_global_attenuation()

    def get_global_attenuation(self):
        replies = self._telnet_query("ATT?")
        replies = replies.split()
        replies = map(float, replies)
        return replies

    def set_channel_attenuation(self, channel, attenuation):
        self._check_attenuation(attenuation)
        self._check_channel(channel)
        if type(channel) == str:
            channel_dict = {"D": 1, "C": 2, "B": 3, "A": 4}
            channel = channel.upper()
            channel = channel_dict[channel]
        else:
            raise TypeError
        channel = str(channel)
        self._telnet_query(":CHAN:"+channel+":SetAtt:" + str(attenuation))
        channel = int(channel)
        return self.get_channel_attenuation(channel)

    def get_channel_attenuation(self, bpm_channel):
        """
        
        Args:
             bpm_channel (str or number): The channel of the attenuator to use. This is either in native values of 
             1,2,3,4, or bpm labels of A, B, C, D.
        
        Returns:
             float: Value of the attenuator on that channel.
        """
        self._check_channel(bpm_channel)
        if type(bpm_channel) == str:
            channel_dict = {"D": 1, "C": 2, "B": 3, "A": 4}
            atten_channel = channel_dict[bpm_channel.upper()]
            command = ''.join((":CHAN:" + str(atten_channel) + ":Att?"))
        else:
            command = ''.join((":CHAN:" + str(bpm_channel) + ":Att?"))
        # print 'Command = ', command
        reply = self._telnet_query(command)
        for md in range(10):
            if not reply:  # Checking for an empty string.
                print 'Got nothing back .... Trying again.'
                reply = self._telnet_query(command)
                sleep(0.5)
            else:
                if md > 0:
                    print 'Get Channel reply = ', reply
                break
        return float(reply)
