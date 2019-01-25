from ProgrammableAttenuator import *
import telnetlib
#from pkg_resources import require
#require("numpy")
import numpy as np


class Simulated_Prog_Atten(Generic_Prog_Atten):

    def __init__(self):
        self.A = 0
        self.B = 0
        self.C = 0
        self.D = 0

    def __del__(self):
        pass

    def _check_attenuation(self, attenuation):
        if type(attenuation) != float and type(attenuation) != int \
                and np.float64 != np.dtype(attenuation) and np.int64 != np.dtype(attenuation):
            raise TypeError
        elif attenuation > 95 or attenuation < 0:
            raise ValueError

    def _check_channel(self, channel):
        if type(channel) == int:
            while channel not in [1, 2, 3, 4]:
                raise ValueError
        else:
            raise TypeError

    def get_device_id(self):
        return "Simulated programmable attenuator device"

    def set_global_attenuation(self, attenuation):
        self._check_attenuation(attenuation)
        self.A = attenuation
        self.B = attenuation
        self.C = attenuation
        self.D = attenuation

    def get_global_attenuation(self):
        return self.A, self.B, self.C, self.D

    def set_channel_attenuation(self, channel, attenuation):

        self._check_attenuation(attenuation)
        self._check_channel(channel)

        if channel == 1:
            self.A = attenuation
        elif channel == 2:
            self.B = attenuation
        elif channel == 3:
            self.C = attenuation
        elif channel == 4:
            self.D = attenuation

    def get_channel_attenuation(self, channel):
        self._check_channel(channel)
        if channel == 1:
            return self.A
        elif channel == 2:
            return self.B
        elif channel == 3:
            return self.C
        elif channel == 4:
            return self.D
