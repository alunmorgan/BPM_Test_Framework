from framework_requires import BaseTestClass
import unittest
from mock import patch
from Simulated_BPMDevice import *
import RFSignalGenerators


class ExpectedDataTestNoGateNoAttentuator(BaseTestClass):

    @classmethod
    def setUpClass(cls):
        # Stuff you only run once
        super(ExpectedDataTestNoGateNoAttentuator, cls).setUpClass()

    @patch("RFSignalGenerators.Simulated_RFSigGen")
    def setUp(self, mock_rf_dev):
        # Stuff you run before each test
        self.simulator_attenuation = 12
        self.test_output_values = [-100]
        self.current = 1000 * 1.1193 ** (self.test_output_values[0] - self.simulator_attenuation)
        mock_rf_dev.get_output_power.return_value = self.test_output_values
        self.simbpm = SimulatedBPMDevice(mock_rf_dev)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        # Stuff you want to run after each test
        pass

    def test_get_X_position(self):
        self.assertEqual(self.simbpm.get_X_position(), 0.0)

    def test_get_Y_position(self):
        self.assertEqual(self.simbpm.get_Y_position(), 0.0)

    def test_get_beam_curent(self):
        self.assertEqual(self.simbpm.get_beam_current(), self.current)

    def test_get_input_power(self):
        self.assertEqual(self.simbpm.get_input_power(), self.test_output_values[0] - self.simulator_attenuation)

    def test_get_raw_BPM_buttons(self):
        a_raw, b_raw, c_raw, d_raw = self.simbpm.get_raw_BPM_buttons()
        self.assertEqual(a_raw, 1000 * self.current)
        self.assertEqual(b_raw, 1000 * self.current)
        self.assertEqual(c_raw, 1000 * self.current)
        self.assertEqual(d_raw, 1000 * self.current)

    def test_get_normalised_BPM_buttons(self):
        a_raw, b_raw, c_raw, d_raw = self.simbpm.get_normalised_BPM_buttons()
        self.assertEqual(a_raw, 1)
        self.assertEqual(b_raw, 1)
        self.assertEqual(c_raw, 1)
        self.assertEqual(d_raw, 1)

    def test_get_device_ID(self):
        self.assertEqual(self.simbpm.get_device_ID(), "Simulated BPM Device")

    def test_get_ADC_sum(self):
        self.assertEqual(self.simbpm.get_ADC_sum(), 4000 * self.current)

    def test_get_input_tolerance(self):
        self.assertEqual(self.simbpm.get_input_tolerance(), -40)


class ExpectedDataTestWithGateNoAttentuator(BaseTestClass):

    @classmethod
    def setUpClass(cls):
        # Stuff you only run once
        super(ExpectedDataTestWithGateNoAttentuator, cls).setUpClass()

    @patch("Gate_Source.Simulated_GateSource")
    @patch("RFSignalGenerators.Simulated_RFSigGen")
    def setUp(self, mock_rf_dev, mock_gate):
        # Stuff you run before each test
        self.simulator_attenuation = 12
        self.simulated_rf_output_power = [-100]
        duty_cycle = 0.5  # Between 0 and 1
        mock_rf_dev.get_output_power.return_value = self.simulated_rf_output_power
        mock_gate.get_modulation_state.return_value = True
        mock_gate.get_pulse_dutycycle.return_value = duty_cycle
        self.expected_input_power = float(self.simulated_rf_output_power -
                                          np.absolute(20 * np.log10(duty_cycle)) -
                                          self.simulator_attenuation)
        self.current = 1000 * 1.1193 ** self.expected_input_power
        self.simbpm = SimulatedBPMDevice(mock_rf_dev, mock_gate)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        # Stuff you want to run after each test
        pass

    def test_get_X_position(self):
        self.assertEqual(self.simbpm.get_X_position(), 0.0)

    def test_get_Y_position(self):
        self.assertEqual(self.simbpm.get_Y_position(), 0.0)

    def test_get_beam_curent(self):
        self.assertEqual(self.simbpm.get_beam_current(), self.current)

    def test_get_input_power(self):
        self.assertEqual(self.simbpm.get_input_power(), self.expected_input_power)

    def test_get_raw_BPM_buttons(self):
        a_raw, b_raw, c_raw, d_raw = self.simbpm.get_raw_BPM_buttons()
        self.assertEqual(a_raw, 1000 * self.current)
        self.assertEqual(b_raw, 1000 * self.current)
        self.assertEqual(c_raw, 1000 * self.current)
        self.assertEqual(d_raw, 1000 * self.current)

    def test_get_normalised_BPM_buttons(self):
        a_raw, b_raw, c_raw, d_raw = self.simbpm.get_normalised_BPM_buttons()
        self.assertEqual(a_raw, 1)
        self.assertEqual(b_raw, 1)
        self.assertEqual(c_raw, 1)
        self.assertEqual(d_raw, 1)

    def test_get_device_ID(self):
        self.assertEqual(self.simbpm.get_device_ID(), "Simulated BPM Device")

    def test_get_ADC_sum(self):
        self.assertEqual(self.simbpm.get_ADC_sum(), 4000 * self.current)

    def test_get_input_tolerance(self):
        self.assertEqual(self.simbpm.get_input_tolerance(), -40)


class ExpectedDataTestWithGateWithAttenuator(BaseTestClass):

    @classmethod
    def setUpClass(cls):
        # Stuff you only run once
        super(ExpectedDataTestWithGateWithAttenuator, cls).setUpClass()

    @patch("ProgrammableAttenuator.Simulated_Prog_Atten")
    @patch("Gate_Source.Simulated_GateSource")
    @patch("RFSignalGenerators.Simulated_RFSigGen")
    def setUp(self, mock_rf_dev, mock_gate, mock_atten):
        # Stuff you run before each test
        self.simulator_attenuation = 12
        self.simulated_rf_output_power = [-100]
        duty_cycle = 0.5  # Between 0 and 1
        a_attenuator = 10
        b_attenuator = 5
        c_attenuator = 12
        d_attenuator = 10
        mock_rf_dev.get_output_power.return_value = self.simulated_rf_output_power
        mock_gate.get_modulation_state.return_value = True
        mock_gate.get_pulse_dutycycle.return_value = duty_cycle
        mock_atten.get_global_attenuation.return_value = a_attenuator, b_attenuator, c_attenuator, d_attenuator
        expected_input_power = float(self.simulated_rf_output_power -
                                          np.absolute(20 * np.log10(duty_cycle)) -
                                          self.simulator_attenuation)
        self.a_pwr = 10 ** ((expected_input_power - 6 - a_attenuator) / 10)  #Convert to mW so the channels can be summed
        self.b_pwr = 10 ** ((expected_input_power - 6 - b_attenuator) / 10)
        self.c_pwr = 10 ** ((expected_input_power - 6 - c_attenuator) / 10)
        self.d_pwr = 10 ** ((expected_input_power - 6 - d_attenuator) / 10)
        self.expected_input_power = 10 * np.log10(self.a_pwr + self.b_pwr + self.c_pwr + self.d_pwr)
        self.current = 1000 * 1.1193 ** self.expected_input_power
        self.simbpm = SimulatedBPMDevice(mock_rf_dev, mock_gate, mock_atten)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        # Stuff you want to run after each test
        pass

    def test_get_X_position(self):
        self.assertEqual(self.simbpm.get_X_position(), 0.0)

    def test_get_Y_position(self):
        self.assertEqual(self.simbpm.get_Y_position(), 0.0)

    def test_get_beam_curent(self):
        self.assertLess(abs(self.simbpm.get_beam_current() - self.current),
                        1E-6 * max(abs(self.simbpm.get_beam_current()), abs(self.current)))

    def test_get_input_power(self):
        self.assertLess(abs(self.simbpm.get_input_power() - self.expected_input_power),
                        1E-6 * max(abs(self.simbpm.get_input_power()), abs(self.expected_input_power)))

    def test_get_raw_BPM_buttons(self):
        a_raw, b_raw, c_raw, d_raw = self.simbpm.get_raw_BPM_buttons()
        total_power_mW = self.a_pwr + self.b_pwr + self.c_pwr + self.d_pwr
        a_signal = 1000 * self.current * self.a_pwr / total_power_mW
        b_signal = 1000 * self.current * self.b_pwr / total_power_mW
        c_signal = 1000 * self.current * self.c_pwr / total_power_mW
        d_signal = 1000 * self.current * self.d_pwr / total_power_mW
        self.assertLess(abs(a_raw - a_signal),
                        max(abs(a_raw), abs(a_signal)))
        self.assertLess(abs(b_raw - b_signal),
                        max(abs(b_raw), abs(b_signal)))
        self.assertLess(abs(c_raw - c_signal),
                        max(abs(c_raw), abs(c_signal)))
        self.assertLess(abs(d_raw - d_signal),
                        max(abs(d_raw), abs(d_signal)))

    def test_get_normalised_BPM_buttons(self):
        a_raw, b_raw, c_raw, d_raw = self.simbpm.get_normalised_BPM_buttons()
        self.assertEqual(a_raw, 1)
        self.assertEqual(b_raw, 1)
        self.assertEqual(c_raw, 1)
        self.assertEqual(d_raw, 1)

    def test_get_device_ID(self):
        self.assertEqual(self.simbpm.get_device_ID(), "Simulated BPM Device")

    def test_get_ADC_sum(self):
        total_power_mW = self.a_pwr + self.b_pwr + self.c_pwr + self.d_pwr
        total_adc = (1000 * self.current * self.a_pwr / total_power_mW +
                    1000 * self.current * self.b_pwr / total_power_mW +
                    1000 * self.current * self.c_pwr / total_power_mW +
                    1000 * self.current * self.d_pwr / total_power_mW)
        self.assertLess(abs(self.simbpm.get_ADC_sum() - total_adc),
                        1E-6 * max(abs(self.simbpm.get_ADC_sum()), abs(total_adc)))

    def test_get_input_tolerance(self):
        self.assertEqual(self.simbpm.get_input_tolerance(), -40)

if __name__ == "__main__":
        unittest.main()
