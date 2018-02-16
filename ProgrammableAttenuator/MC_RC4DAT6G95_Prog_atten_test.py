from framework_requires import BaseTestClass
import unittest
from mock import patch
import ProgrammableAttenuator

class ExpectedDataTest(BaseTestClass):

    @classmethod
    def setUpClass(cls):
        # Stuff you only run once
        super(ExpectedDataTest, cls).setUpClass()

    @patch("ProgrammableAttenuator.telnetlib.Telnet")
    @patch("ProgrammableAttenuator.MC_RC4DAT6G95_Prog_Atten.get_device_id", return_value="IT CLKGEN")
    def setUp(self, mock_device, mock_telnet):
        # Stuff you run before each test
        self.PA_test_inst = ProgrammableAttenuator.MC_RC4DAT6G95_Prog_Atten("0", 0, 0)
        unittest.TestCase.setUp(self)

    @patch("ProgrammableAttenuator.telnetlib.Telnet")
    def tearDown(self, mock_telnet):
        # Stuff you want to run after each test
        pass

    def test_check_attenuation_errors_if_invalid_input_values_used(self):
        self.assertRaises(ValueError, self.PA_test_inst._check_attenuation, -11)
        self.assertRaises(TypeError, self.PA_test_inst._check_attenuation, "FF")

    def test_check_channel_errors_if_invalid_input_values_used(self):
        self.assertRaises(ValueError, self.PA_test_inst._check_channel, -11)
        self.assertRaises(ValueError, self.PA_test_inst._check_channel, "FF")

    def test_set_global_attenuation_errors_if_invalid_input_values_used(self):
        self.assertRaises(ValueError, self.PA_test_inst.set_global_attenuation, -11)
        self.assertRaises(TypeError, self.PA_test_inst.set_global_attenuation, "FF")

    def test_set_channel_attenuation_errors_if_invalid_input_values_used(self):
        self.assertRaises(TypeError, self.PA_test_inst.set_global_attenuation, ("D", 22))
        self.assertRaises(TypeError, self.PA_test_inst.set_global_attenuation, (33, 22))


