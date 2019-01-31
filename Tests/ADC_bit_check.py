import time
import json


def adc_test(
             test_system_object,
             frequency,
             output_power_level=-20,
             settling_time=1,
             sub_directory=""):
    """Compares the signals from the ADCs while a sine wave excitation is input.

    The RF signal is turned off, and then different parameters are measured from the BPM. 

    Args:
        test_system_object (System Obj): Object capturing the system losses and hardware ids.
        frequency (float): Output frequency for the tests, set as a float that will use the assumed units of MHz.
        output_power_level (float): output power level for the tests. dBm is assumed.
        settling_time (float): Time in seconds, that the program will wait in between
            setting an  output power on the RF, and reading the values of the BPM. 
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
    """
    test_name, set_output_power = test_system_object.test_initialisation(test_name=__name__,
                                                                         frequency=frequency,
                                                                         output_power_level=output_power_level)
    test_system_object.BPM.set_internal_state({'agc': 'AGC off',
                                               'delta': 0,
                                               'offset': 0,
                                               'switches': 'Manual',
                                               'switch_state': test_system_object.BPM.switch_straight,
                                               'attenuation': 0,
                                               'dsc': 'Unity gains',
                                               'ft_state': 'Enabled'})
    ft_state, agc, delta, offset_wf, switches, switch_state, bpm_attenuation, dsc = \
        test_system_object.BPM.get_internal_state()

    test_system_object.RF.turn_on_RF()
    # Wait for signal to settle
    time.sleep(settling_time)
    # Gets 1024 samples for each ADC.
    time_tmp, data_tmp = test_system_object.BPM.get_adc_data(16)  # record data
    # turn off the RF
    test_system_object.RF.turn_off_RF()

    data_out = {'test_name': test_name,
                'rf_hw': test_system_object.rf_id,
                'bpm_hw': test_system_object.bpm_id,
                'bpm_agc': agc,
                'bpm_switching': switches,
                'bpm_dsc': dsc,
                'bpm_attenuation': bpm_attenuation,
                'n_bits': test_system_object.BPM.adc_n_bits,
                'n_adc': test_system_object.BPM.num_adcs,
                'data': data_tmp,
                'time': list(time_tmp)
                }

    with open(sub_directory + "ADC_bit_check_data.json", 'w') as write_file:
        json.dump(data_out, write_file)
