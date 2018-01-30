from framework_requires import BaseTestClass
import unittest
from mock import patch
import BPMDevice


def mock_get_device_id():
    return "Libera Electron BPM with the Epics ID \"TS-DI-EBPM-00:\" and the MAC Address \"00:d0:50:31:03:b9\""


def mocked_bpm_replies(pv):
    if pv == "SA:POWER":
        return -100.0
    elif pv == "SA:CURRENT":
        return 10.0
    elif pv == "SA:A":
        return 800.0
    elif pv == "SA:B":
        return 900.0
    elif pv == "SA:C":
        return 1100.0
    elif pv == "SA:D":
        return 1200.0
    elif pv == "SA:AN":
        return 0.8
    elif pv == "SA:BN":
        return 0.9
    elif pv == "SA:CN":
        return 1.1
    elif pv == "SA:DN":
        return 1.2
    elif pv == "SA:X":
        return 100.0
    elif pv == "SA:Y":
        return -100.0


class ExpectedDataTest(BaseTestClass):

    @classmethod
    def setUpClass(cls):
        # Stuff you only run once
        super(ExpectedDataTest, cls).setUpClass()

    @patch("BPMDevice.ElectronBPMDevice._read_epics_pv")
    @patch("BPMDevice.ElectronBPMDevice._get_mac_address", return_value='00:d0:50:31:03:b9')
    def setUp(self, mac_mock, epics_mock):
        # Stuff you run before each test
        self.BPM_test_inst = BPMDevice.ElectronBPMDevice('TS-DI-EBPM-00:')
        unittest.TestCase.setUp(self)

    def tearDown(self):
        pass
        # Stuff you want to run after each test

    def test_mac_address(self):
        self.assertEqual(self.BPM_test_inst.mac_address, "00:d0:50:31:03:b9")

    @patch("BPMDevice.ElectronBPMDevice.get_device_id", side_effect=mock_get_device_id)
    def test_device_ID(self, mock_dev_id):
        self.assertEqual(self.BPM_test_inst.get_device_id(),
                         "Libera Electron BPM with the Epics ID \"TS-DI-EBPM-00:\"" +
                         " and the MAC Address \"00:d0:50:31:03:b9\"")
        self.assertTrue(mock_dev_id.called)

    @patch("BPMDevice.ElectronBPMDevice._read_epics_pv", side_effect=mocked_bpm_replies)
    def test_get_BPM_power(self, mock_replies):
        self.assertEqual(self.BPM_test_inst.get_input_power(), -100)
        self.assertTrue(mock_replies.called)

    @patch("BPMDevice.ElectronBPMDevice._read_epics_pv", side_effect=mocked_bpm_replies)
    def test_get_BPM_current(self, mock_replies):
        self.assertEqual(self.BPM_test_inst.get_beam_current(), 10)
        self.assertTrue(mock_replies.called)

    @patch("BPMDevice.ElectronBPMDevice._read_epics_pv", side_effect=mocked_bpm_replies)
    def test_get_raw_BPM_buttons(self, mock_replies):
        self.assertEqual(self.BPM_test_inst.get_raw_bpm_buttons(), (800, 900, 1100, 1200))
        self.assertTrue(mock_replies.called)

    @patch("BPMDevice.ElectronBPMDevice._read_epics_pv", side_effect=mocked_bpm_replies)
    def test_get_normalised_BPM_buttons(self, mock_replies):
        self.assertEqual(self.BPM_test_inst.get_normalised_bpm_buttons(), (0.8, 0.9, 1.1, 1.2))
        self.assertTrue(mock_replies.called)

    @patch("BPMDevice.ElectronBPMDevice._read_epics_pv", side_effect=mocked_bpm_replies)
    def test_get_X_position(self, mock_replies):
        self.assertEqual(self.BPM_test_inst.get_x_position(), 100)
        self.assertTrue(mock_replies.called)

    @patch("BPMDevice.ElectronBPMDevice._read_epics_pv", side_effect=mocked_bpm_replies)
    def test_get_Y_position(self, mock_replies):
        self.assertEqual(self.BPM_test_inst.get_y_position(), -100)
        self.assertTrue(mock_replies.called)

    def test_get_input_tolerance(self):
        self.assertEqual(self.BPM_test_inst.get_input_tolerance(), -20)

    @patch("BPMDevice.ElectronBPMDevice._read_epics_pv", side_effect=mocked_bpm_replies)
    def test_get_ADC_sum(self, mock_replies):
        self.assertEqual(self.BPM_test_inst.get_adc_sum(), 4000)


if __name__ == "__main__":
    unittest.main()
