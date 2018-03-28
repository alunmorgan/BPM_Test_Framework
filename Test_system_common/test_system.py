from math import floor

class TestSystem:
    """This captures the behaviour of the system due to cabling losses"""

    def __init__(self, rf_hw, gate_hw, trigger_hw, bpm_hw):
        """Initialises the test system object with information about cable losses"""
        self.channel1_loss = 16.55
        self.channel2_loss = 16.32
        self.channel3_loss = 16.40
        self.channel4_loss = 16.37
        """Returns the minimum loss between the RF source and the BPM input.
            This is required to make sure that nothing gets too much power 
            put into it, which would be a risk if the average was used."""
        self.loss = min(self.channel1_loss, self.channel2_loss,
                        self.channel3_loss, self.channel4_loss)
        self.rf_hw = rf_hw.get_device_id()
        self.gate_hw = gate_hw.get_device_id()
        self.trigger_hw = trigger_hw.get_device_id()
        self.bpm_hw = bpm_hw.get_device_id()

    def test_initialisation(self, test_name, rf_object, prog_atten_object, bpm_object, frequency,
                            power_level, external_attenuation=0):
        # Formats the test name and tells the user the test has started
        test_name = test_name.rsplit("Tests.")[1]
        test_name = test_name.replace("_", " ")
        print("Starting test \"" + test_name + "\"")

        # Initial setup of the RF system.
        rf_object.turn_off_RF()
        rf_object.set_frequency(frequency)
        # Forcing to be an int as decimal points will cause the command sent to fail
        if power_level < bpm_object.max_input:
            rf_object.set_output_power(int(floor(power_level + self.loss)))
            prog_atten_object.set_global_attenuation(external_attenuation)
            rf_object.turn_on_RF()
        else:
            raise ValueError('Input power level dangerously high')

        return test_name



