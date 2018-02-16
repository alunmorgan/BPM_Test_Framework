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

    @patch("Trigger_Source.ITechBL12HI_trigsrc.get_device_id", return_value="IT CLKGEN")
    @patch("Trigger_Source.ITechBL12HI_trigsrc.turn_off_RF")
    def setUp(self, mock_rf, mock_device):
        # Stuff you run before each test
        self.GS_test_inst = Trigger_Source.ITechBL12HI_trigsrc("0", 0, 0)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        # Stuff you want to run after each test
        pass

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("TEST"))
    def test_get_device_id_errors_with_bad_input(self, mock_telnet_query):
        self.assertRaises(ValueError, self.GS_test_inst.get_device_id)
