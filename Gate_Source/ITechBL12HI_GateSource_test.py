from framework_requires import BaseTestClass
import unittest
from mock import patch
import Gate_Source

# Checks the simple get requests against the criteria set here

output = "1"
period = "3uS"
dutycycle = "0.03uS"


def return_ok_values(input_string):
    return input_string, "OK"


def return_bad_values(input_string):
    return input_string, "ERR"


def mocked_itech_replies(_1, _2, _3, input):
    global output, period, dutycycle

    if input == "MOD:STAT?":
        return output,
    elif input == "PULM:PER?":
        return period
    elif input == "PULM:WIDT?":
        return dutycycle

    # for set tests to be implemented, reg ex or something similar will go here, to scan
    # the input string. This will then be used to set the globals listed above. Then they
    # can be read back using the 'mocked_itech_replies' function.


class ExpectedDataTest(BaseTestClass):

    @classmethod
    def setUpClass(cls):
        # Stuff you only run once
        super(ExpectedDataTest, cls).setUpClass()

    @patch("Gate_Source.ITechBL12HI_GateSource.get_modulation_state", return_value=False)
    @patch("Gate_Source.ITechBL12HI_GateSource.get_device_id", return_value="IT CLKGEN")
    @patch("Gate_Source.ITechBL12HI_GateSource.set_pulse_dutycycle")
    def setUp(self, mock_pulse, mock_device, mock_telnet_query):
        # Stuff you run before each test
        self.GS_test_inst = Gate_Source.ITechBL12HI_GateSource("0", 0, 0)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        # Stuff you want to run after each test
        pass

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("TEST"))
    def test_set_pulse_dutycycle_errors_with_negative_input(self, mock_telnet_query):
        self.assertRaises(ValueError, self.GS_test_inst.set_pulse_dutycycle, -0.1)

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("TEST"))
    def test_set_pulse_dutycycle_errors_with_input_greater_than_one(self, mock_telnet_query):
        self.assertRaises(ValueError, self.GS_test_inst.set_pulse_dutycycle, 1.1)

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("TEST"))
    def test_set_pulse_dutycycle_errors_with_invalid_input_type(self, mock_telnet_query):
        self.assertRaises(TypeError, self.GS_test_inst.set_pulse_dutycycle, "0.5")

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("TEST"))
    def test_set_pulse_period_errors_with_negative_input(self, mock_telnet_query):
        self.assertRaises(ValueError, self.GS_test_inst.set_pulse_period, -0.1)

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("TEST"))
    def test_set_pulse_period_errors_with_invalid_input_type(self, mock_telnet_query):
        self.assertRaises(TypeError, self.GS_test_inst.set_pulse_period, "1.1")

#######################################################
    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("TEST"))
    def test_turn_on_modulation_works_with_expected_output(self, mock_query):
        self.assertEqual(self.GS_test_inst.turn_on_modulation(), True)

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_bad_values("TEST"))
    def test_turn_on_modulation_errors_with_bad_return_value(self, mock_query):
        self.assertRaises(self.GS_test_inst.turn_on_modulation)

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("TEST"))
    def test_turn_off_modulation_works_with_expected_output(self, mock_query):
        self.assertEqual(self.GS_test_inst.turn_off_modulation(), False)

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_bad_values("TEST"))
    def test_turn_off_modulation_errors_with_bad_return_value(self, mock_query):
        self.assertRaises(self.GS_test_inst.turn_off_modulation)

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("0.5"))
    def test_set_pulse_dutycycle_errors_if_invalid_input_type_used(self, mock_query):
        self.assertRaises(TypeError, self.GS_test_inst.set_pulse_dutycycle, "0.01")

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("50 %"))
    def test_get_dutycycle_return_values_if_expected_input_types_used(self, mock_query):
        self.assertEqual(self.GS_test_inst.get_pulse_dutycycle(), 0.5)

    @patch("common_device_functions.ITechBL12HI_common.telnet_query", return_value=return_ok_values("50 MHz"))
    def test_get_pulse_period_return_values_if_expected_input_types_used(self, mock_query):
        self.assertEqual(self.GS_test_inst.get_pulse_period(), (0.02, "us"))


if __name__ == "__main__":
        unittest.main()
