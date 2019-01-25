import numpy as np
import time
import json


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
    test_name = test_system_object.test_initialisation(test_name=__name__,
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

    num_repeat_points = 10
    data = []
    # B_data = []
    # C_data = []
    # D_data = []
    adj_before = []
    adj_after = []
    # B_adj_before = []
    # B_adj_after = []
    # C_adj_before = []
    # C_adj_after = []
    # D_adj_before = []
    # D_adj_after = []
    data_std = []
    data_max = []
    data_mean = []
    # Start test
    test_system_object.RF.turn_on_RF()
    # Wait for system to settle
    time.sleep(settling_time)
    # Gradually reducing the power level
    # level_ind = 0
    bpm_input_power = []
    output_power = []
    for step in range(number_of_attenuation_steps):
        bpm_input_power.append(int(round(test_system_object.BPM.get_input_power())))
        output_power.append(output_power_level - step * attenuation_step_size)
        data.append([])
        # B_data.append([])
        # C_data.append([])
        # D_data.append([])
        adj_before.append([])
        adj_after.append([])
        # B_adj_before.append([])
        # B_adj_after.append([])
        # C_adj_before.append([])
        # C_adj_after.append([])
        # D_adj_before.append([])
        # D_adj_after.append([])
        # data_adj.append([])
        # data_std.append([])
        # data_max.append([])
        # data_mean.append([])
        # data_adj_before = np.empty((1024, test_system_object.BPM.num_adcs))
        # data_adj_after = np.empty((1024, test_system_object.BPM.num_adcs))

        _1, adj_before[step] = test_system_object.BPM.get_adc_data(test_system_object.BPM.adc_n_bits)

        time.sleep(settling_time)  # Wait for signal to settle
        glob_atten = test_system_object.ProgAtten.get_global_attenuation()
        if glob_atten[0] - glob_atten[1] > 0.00001 or glob_atten[0] - glob_atten[2] > 0.00001 or \
           glob_atten[0] - glob_atten[3] > 0.00001:
            raise ValueError('The four attenuation levels are not set to the same value')

        test_system_object.ProgAtten.set_global_attenuation(glob_atten[0] + attenuation_step_size)

        _1, adj_after[step] = test_system_object.BPM.get_adc_data(test_system_object.BPM.adc_n_bits)

        # data_adj[level_ind].append(list(np.max(data_adj_after, axis=0) - np.max(data_adj_before, axis=0))) #+ data_adj[level_ind - 1, :]
        bpm_atten = test_system_object.BPM.get_attenuation()
        test_system_object.BPM.set_attenuation(bpm_atten - attenuation_step_size)
        time.sleep(settling_time)  # Wait for signal to settle
        # Gets 1024 samples for each ADC.
        # for lec in range(test_system_object.BPM.num_adcs):
        # A_data[level_ind].append([])
        # B_data[level_ind].append([])
        # C_data[level_ind].append([])
        # D_data[level_ind].append([])
            # data_std[level_ind].append([lec])
            # data_max[level_ind].append([lec])

        # data_std_1_temp = []
        # data_std_2_temp = []
        # data_std_3_temp = []
        # data_std_4_temp = []
        # data_max_1_temp = []
        # data_max_2_temp = []
        # data_max_3_temp = []
        # data_max_4_temp = []
        # data_mean_1_temp = []
        # data_mean_2_temp = []
        # data_mean_3_temp = []
        # data_mean_4_temp = []

        for nw in range(num_repeat_points):
            # record data
            time_tmp, data_tmp = test_system_object.BPM.get_adc_data(test_system_object.BPM.adc_n_bits)
            data[step].append(list(data_tmp))
            # B_data[step].append(list(data2_tmp[1]))
            # C_data[step].append(list(data3_tmp[2]))
            # D_data[step].append(list(data4_tmp[3]))
        #     data_std_1_temp.append(np.std(data1_tmp))
        #     data_std_2_temp.append(np.std(data2_tmp))
        #     data_std_3_temp.append(np.std(data3_tmp))
        #     data_std_4_temp.append(np.std(data4_tmp))
        #     data_max_1_temp.append(np.max(data1_tmp))
        #     data_max_2_temp.append(np.max(data2_tmp))
        #     data_max_3_temp.append(np.max(data3_tmp))
        #     data_max_4_temp.append(np.max(data4_tmp))
        #     data_mean_1_temp.append(np.mean(data1_tmp))
        #     data_mean_2_temp.append(np.mean(data2_tmp))
        #     data_mean_3_temp.append(np.mean(data3_tmp))
        #     data_mean_4_temp.append(np.mean(data4_tmp))
        # data_std[level_ind].append(np.std(data_mean_1_temp))
        # data_std[level_ind].append(np.std(data_mean_2_temp))
        # data_std[level_ind].append(np.std(data_mean_3_temp))
        # data_std[level_ind].append(np.std(data_mean_4_temp))
        # data_max[level_ind].append(np.mean(data_max_1_temp))
        # data_max[level_ind].append(np.mean(data_max_2_temp))
        # data_max[level_ind].append(np.mean(data_max_3_temp))
        # data_max[level_ind].append(np.mean(data_max_4_temp))
        # data_mean[level_ind].append(np.mean(data_mean_1_temp))
        # data_mean[level_ind].append(np.mean(data_mean_2_temp))
        # data_mean[level_ind].append(np.mean(data_mean_3_temp))
        # data_mean[level_ind].append(np.mean(data_mean_4_temp))

        # level_ind = level_ind + 1

    # turn off the RF
    test_system_object.RF.turn_off_RF()
    # data_max = np.mean(np.max(data, axis=1), axis=2)
    # data_std = np.std(np.max(data, axis=1), axis=2)
    # data_corrected = data_max - data_adj
    data_out = {'test_name': test_name,
                'rf_id': test_system_object.rf_id,
                'bpm_id': test_system_object.bpm_id,
                'prog_atten_id': test_system_object.prog_atten_id,
                'frequency': frequency,
                'settling_time': settling_time,
                'output_power': output_power,
                'bpm_input_power': bpm_input_power,
                'bpm_agc': test_system_object.BPM.agc,
                'bpm_switching': test_system_object.BPM.switches,
                'bpm_dsc': test_system_object.BPM.dsc,
                'n_bits': test_system_object.BPM.adc_n_bits,
                'n_adc': test_system_object.BPM.num_adcs,
                'data': data,
                'adj_before': adj_before,
                'adj_after': adj_after
                }







    # data_out = {'output_power': output_power,
    #             'bpm_input_power': bpm_input_power,
    #             'data': data,
    #             'data_max': data_max,
    #             'data_std': data_std,
    #             'data_mean': data_mean,
    #             'data_adj': data_adj,
    #             'n_bits': test_system_object.BPM.adc_n_bits,
    #             'n_adc': test_system_object.BPM.num_adcs,
    #             'bpm_agc': test_system_object.BPM.agc,
    #             'bpm_switching': test_system_object.BPM.switches,
    #             'bpm_dsc': test_system_object.BPM.dsc,
    #             'test_name': test_name,
    #             'rf_id': test_system_object.rf_id,
    #             'prog_atten_id': test_system_object.prog_atten_id,
    #             'bpm_id': test_system_object.bpm_id}

    with open(sub_directory + "ADC_int_atten_sweep_data.json", 'w') as write_file:
        json.dump(data_out, write_file)
