import numpy as np
import time
import json
import sys
from helper_functions.helper_calc_functions import sa_data_to_dict


def adc_int_atten_sweep_test(
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
        output_power_level (float): output power level for the test. dBm is assumed.
        settling_time (float): Time in seconds, that the program will wait in between
            setting an  output power on the RF, and reading the values of the BPM.
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
        float array: X ADC data read from the BPM
        float array: Y ADC data read from the BPM
    """
    attenuation_step_size = 2
    number_of_attenuation_steps = 10
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

    num_repeat_points = 10
    data = []
    adj_before = []
    adj_after = []
    # Start test
    test_system_object.RF.turn_on_RF()
    # Wait for system to settle
    time.sleep(settling_time)
    # Gradually reducing the power level
    bpm_input_power = []
    output_power = []

    for step in range(number_of_attenuation_steps):
        bpm_input_power.append(int(round(test_system_object.BPM.get_input_power())))
        output_power.append(output_power_level - step * attenuation_step_size)
        data.append([])
        adj_before.append([])
        adj_after.append([])

        sa_a_times_ab, sa_a_data_ab, sa_b_times_ab, sa_b_data_ab, \
            sa_c_times_ab, sa_c_data_ab, sa_d_times_ab, sa_d_data_ab = \
            test_system_object.BPM.get_sa_data(num_repeat_points)
        adj_before[step] = sa_data_to_dict(sa_a_times_ab, sa_a_data_ab, sa_b_times_ab, sa_b_data_ab,
                                           sa_c_times_ab, sa_c_data_ab, sa_d_times_ab, sa_d_data_ab)
        time.sleep(settling_time)  # Wait for signal to settle
        glob_atten = test_system_object.ProgAtten.get_global_attenuation()
        if glob_atten[0] - glob_atten[1] > 0.00001 or glob_atten[0] - glob_atten[2] > 0.00001 or \
           glob_atten[0] - glob_atten[3] > 0.00001:
            raise ValueError('The four attenuation levels are not set to the same value')

        test_system_object.ProgAtten.set_global_attenuation(glob_atten[0] + attenuation_step_size)

        sa_a_times_aa, sa_a_data_aa, sa_b_times_aa, sa_b_data_aa, \
            sa_c_times_aa, sa_c_data_aa, sa_d_times_aa, sa_d_data_aa = \
            test_system_object.BPM.get_sa_data(num_repeat_points)
        adj_after[step] = sa_data_to_dict(sa_a_times_aa, sa_a_data_aa, sa_b_times_aa, sa_b_data_aa,
                                          sa_c_times_aa, sa_c_data_aa, sa_d_times_aa, sa_d_data_aa)
        bpm_atten = test_system_object.BPM.get_attenuation()
        test_system_object.BPM.set_attenuation(bpm_atten - attenuation_step_size)
        time.sleep(settling_time)  # Wait for signal to settle

        # Capture data
        sa_a_times, sa_a_data, sa_b_times, sa_b_data, sa_c_times, sa_c_data, sa_d_times, sa_d_data = \
            test_system_object.BPM.get_sa_data(num_repeat_points)
        data[step] = sa_data_to_dict(sa_a_times, sa_a_data, sa_b_times, sa_b_data,
                                     sa_c_times, sa_c_data, sa_d_times, sa_d_data)

        # print step
        # print number_of_attenuation_steps
        # progress = (step + 1) / number_of_attenuation_steps * 100.
        # sys.stdout.write(('=' * progress) + ('' * (100 - progress)) + ("\r [ %d" % progress + "% ] "))
        # sys.stdout.flush()

    # turn off the RF
    test_system_object.RF.turn_off_RF()

    data_out = {'test_name': test_name,
                'rf_id': test_system_object.rf_id,
                'bpm_id': test_system_object.bpm_id,
                'prog_atten_id': test_system_object.prog_atten_id,
                'frequency': frequency,
                'settling_time': settling_time,
                'output_power': output_power,
                'bpm_input_power': bpm_input_power,
                'bpm_agc': agc,
                'bpm_switching': switches,
                'bpm_dsc': dsc,
                'bpm_attenuation': bpm_attenuation,
                'n_bits': test_system_object.BPM.adc_n_bits,
                'n_adc': test_system_object.BPM.num_adcs,
                'data': data,
                'adj_before': adj_before,
                'adj_after': adj_after
                }

    with open(sub_directory + "ADC_int_atten_sweep_data.json", 'w') as write_file:
        json.dump(data_out, write_file)
