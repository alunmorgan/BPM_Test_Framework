from framework_requires import BaseTestClass
import unittest
import warnings
from mock import patch
import RFSignalGenerators


# Checks the simple get requests against the criteria set here

output = "1"
power_units = "DBM"
power = "-100.0DBM"
frequency = "499,6817682MHz"


def id_return():
    return"IT CLKGEN", "OK"


def freq_return():
    return frequency, "OK"


def output_return():
    return power

def power_return():
    return "-40,00DBM", "OK"

def mocked_itech_replies(input):
    global output, power_units, power, frequency
    if input == "LEV?":
        return power
    elif input == "UNIT:POW?":
        return power_units
    elif input == "FREQ?":
        return frequency
    elif input == "OUTP?":
        return output
    elif input == "*IDN?":
        return "ITCLKGEN"
    elif input == "LEV:LIM?":
        return "-40.00"
    if input == "OUTP OFF":
        return "0"
    elif input == "OUTP ON":
        return "1"

    # for set tests to be implimented, reg ex or something similar will go here, to scan
    # the input string. This will then be used to set the globals listed above. Then they
    # can be read back using the 'mocked_itech_replies' function.


class ExpectedDataTest(BaseTestClass):

    @classmethod
    def setUpClass(cls):
        # Stuff you only run once
        super(ExpectedDataTest, cls).setUpClass()

    @patch("RFSignalGenerators.ITechBL12HI_RFSigGen._telnet_query", side_effect=mocked_itech_replies)
    @patch("RFSignalGenerators.ITechBL12HI_RFSigGen.get_device_ID", return_value="ITCLKGEN")
    @patch("RFSignalGenerators.ITechBL12HI_RFSigGen.turn_off_RF")
    def setUp(self, mock_rf, mock_device, mock_telnet_query):
        # Stuff you run before each test
        self.RF_test_inst = RFSignalGenerators.ITechBL12HI_RFSigGen(ipaddress="192.168.0.0", port=0,
                                                                    timeout=0, limit=-40)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        # Stuff you want to run after each test
        pass

    @patch("RFSignalGenerators.ITechBL12HI_RFSigGen._telnet_query")
    def test_set_frequency_if_invalid_input_types_used(self, mock_telnet_query):
        self.assertRaises(ValueError, self.RF_test_inst.set_frequency, -100)
        self.assertRaises(TypeError, self.RF_test_inst.set_frequency, "100")

    @patch("RFSignalGenerators.ITechBL12HI_RFSigGen._telnet_query", return_value=power_return())
    def test_set_power_if_invalid_input_types_used(self, mock_telnet_query):
        self.assertRaises(TypeError, self.RF_test_inst.set_output_power, "0")
        self.assertWarns(UserWarning, self.RF_test_inst.set_output_power, -39)

    ################################Simple Get requests################################
    @patch("RFSignalGenerators.ITechBL12HI_RFSigGen._telnet_query", return_value=id_return())
    def test_get_device_ID(self, mock_telnet_query):
        self.assertEqual(self.RF_test_inst.get_device_ID(), "IT CLKGEN")

    @patch("RFSignalGenerators.ITechBL12HI_RFSigGen._telnet_query", return_value=output_return())
    def test_get_output_power(self, mock_telnet_query):
        self.assertEqual(self.RF_test_inst.get_output_power(), (-100.0, "-100.0DBM"))

    @patch("RFSignalGenerators.ITechBL12HI_RFSigGen._telnet_query", return_value=freq_return())
    def test_get_frequency(self, mock_telnet_query):
        self.assertEqual(self.RF_test_inst.get_frequency(), (499.6817682, "499,6817682MHz"))

    # @patch("RFSignalGenerators.ITechBL12HI_RFSigGen._telnet_query", side_effect=mocked_itech_replies)
    # def test_turn_off_output_state(self, mock_telnet_query):
    #     self.assertEqual(self.RF_test_inst.turn_off_RF(), False)
    #
    # @patch("RFSignalGenerators.ITechBL12HI_RFSigGen._telnet_query", side_effect=mocked_itech_replies)
    # def test_turn_on_output_state(self, mock_telnet_query):
    #     self.assertEqual(self.RF_test_inst.turn_on_RF(), True)

    @patch("RFSignalGenerators.ITechBL12HI_RFSigGen._telnet_query", side_effect=mocked_itech_replies)
    def test_set_output_power_limit(self, mock_telnet_query):
        self.assertRaises(TypeError, self.RF_test_inst.set_output_power, "0")

    def test_get_output_power_limit(self):
        self.assertEqual(self.RF_test_inst.get_output_power_limit(), (-40, "-40 dBm"))

    def assertWarns(self, warning, callable, *args, **kwds):
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter('always')

            result = callable(*args, **kwds)

            self.assertTrue(any(item.category == warning for item in warning_list))

if __name__ == "__main__":
        unittest.main()