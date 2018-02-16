from framework_requires import BaseTestClass
import unittest
from mock import patch
import Trigger_Source


def return_ok_values(input_string):
    return input_string, "OK"


def return_bad_values(input_string):
    return input_string, "ERR"

output = "1"
period = "3uS"
dutycycle = "0.03uS"
def mocked_itech_replies(input):
    global output, period, dutycycle

    if input == "MOD:STAT?":
        return output
    elif input == "PULM:PER?":
        return period
    elif input == "PULM:WIDT?":
        return dutycycle


class ExpectedDataTest(BaseTestClass):

    @classmethod
    def setUpClass(cls):
        # Stuff you only run once
        super(ExpectedDataTest, cls).setUpClass()

    @patch("Trigger_Source.telnetlib.Telnet")
    @patch("Trigger_Source.agilent33220a_wfmgen.get_device_id",
           return_value="Welcome to Agilent's 33220A Waveform Generator")
    @patch("Trigger_Source.agilent33220a_wfmgen.turn_off_RF")
    def setUp(self, mock_rf, mock_device, mock_telnet):
        # Stuff you run before each test
        self.TS_test_inst = Trigger_Source.agilent33220a_wfmgen("0", 0, 0)
        unittest.TestCase.setUp(self)

    @patch("Trigger_Source.telnetlib.Telnet")
    def tearDown(self, mock_telnet):
        # Stuff you want to run after each test
        pass

    @patch("Trigger_Source.agilent33220a_wfmgen._telnet_query", return_value=return_ok_values("TEST"))
    def test_get_device_id_errors_with_bad_input(self, mock_telnet_query):
        self.assertRaises(ValueError, self.TS_test_inst.get_device_id)

    @patch("Trigger_Source.agilent33220a_wfmgen._telnet_write")
    def test_set_up_trigger_pulse_errors_with_bad_input(self, mock_telnet_write):
        self.assertRaises(TypeError, self.TS_test_inst.set_up_trigger_pulse, "SS")