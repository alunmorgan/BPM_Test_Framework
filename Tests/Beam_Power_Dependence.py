import numpy as np
import time
import json


def beam_power_dependence(
                          test_system_object,
                          frequency,
                          output_power_levels=range(-40, -100, -10),
                          settling_time=0.2,
                          samples=10,
                          sub_directory=""):
    """Tests the relationship between RF output power and values read from the BPM.

    An RF signal is output, and then different parameters are measured from the BPM. 
    The signal is linearly ramped up in dBm at a single frequency. The number of samples to take, 
    and settling time between each measurement can be decided using the arguments. 

    Args:
        test_system_object (System Obj): Object capturing the devices used, system losses and hardware ids.
        frequency (float): Output frequency for the tests, set as a float that will
            use the assumed units of MHz. 
        output_power_levels (list): The desired power levels to run the test at.
                             default value is [-40, -50, -60, -70, -80, -90].
                             The values are floats and dBm is assumed.
        settling_time (float): Time in seconds, that the program will wait in between 
            setting an  output power on the RF, and reading the values of the BPM.
        samples (int): The number of samples to capture at each data point.
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
        float array: Power read at the BPM
        float array: X Positions read from the BPM
        float array: Y Positions read from the BPM
        float array: Standard deviation of X Positions read from the BPM
        float array: Standard deviation Y Positions read from the BPM
    """

    test_name, starting_power = test_system_object.test_initialisation(test_name=__name__,
                                                                       frequency=frequency,
                                                                       output_power_level=output_power_levels[0])
    original_output_power_levels = output_power_levels[:]
    output_power_levels[0] = starting_power
    # Set up BPM for normal operation
    test_system_object.BPM.set_internal_state({'agc': 0, 'attenuation': 35})

    # Build up the arrays where the final values will be saved
    x_pos_raw = []
    y_pos_raw = []
    x_pos_raw_time = []
    y_pos_raw_time = []
    # x_pos_mean = np.array([])
    # y_pos_mean = np.array([])
    # x_pos_std = np.array([])
    # y_pos_std = np.array([])
    input_power = []

    starting_attenuations = test_system_object.ProgAtten.get_global_attenuation()
    if starting_attenuations[0] - starting_attenuations[1] > 0.00001 or \
       starting_attenuations[0] - starting_attenuations[2] > 0.00001 or \
       starting_attenuations[0] - starting_attenuations[3] > 0.00001:
        raise ValueError('The initial attenuation values are not the same value')
    # Perform the test
    x_time_baseline, x_pos_baseline = test_system_object.BPM.get_x_sa_data(samples)  # record X pos
    y_time_baseline, y_pos_baseline = test_system_object.BPM.get_y_sa_data(samples)  # record Y pos

    # x_baseline_mean = np.mean(x_pos_baseline)
    # y_baseline_mean = np.mean(y_pos_baseline)


    test_system_object.RF.turn_on_RF()
    # Wait for signal to settle
    applied_output_power_levels = []
    time.sleep(settling_time)
    for index in output_power_levels:
        # Set attenuator value to give desired power level.
        # As this is a relative adjustment the initial correction for system loss is
        # still valid.
        attenuation_applied = output_power_levels[0] - index
        test_system_object.ProgAtten.set_global_attenuation(starting_attenuations[0] + attenuation_applied)
        temp = test_system_object.ProgAtten.get_global_attenuation()
        applied_output_power_levels.append(output_power_levels[0] - (temp[0] - starting_attenuations[0]))
        time.sleep(settling_time)  # Wait for signal to settle
        # Perform the test
        input_power.append(test_system_object.BPM.get_input_power())
        x_time, x_pos_data = test_system_object.BPM.get_x_sa_data(samples)  # record X pos
        y_time, y_pos_data = test_system_object.BPM.get_y_sa_data(samples)  # record Y pos
        x_pos_raw.append(x_pos_data)
        y_pos_raw.append(y_pos_data)
        x_pos_raw_time.append(x_time)
        y_pos_raw_time.append(y_time)
        # if index == output_power_levels[0]:
        #     x_pos_first = np.mean(x_pos_data)
        #     y_pos_first = np.mean(y_pos_data)
        #     x_pos_mean = [0]
        #     y_pos_mean = [0]
        # else:
        #     x_pos_mean = np.append(x_pos_mean, (np.mean(x_pos_data) - x_pos_first) * 1e3)  # record X pos
        #     y_pos_mean = np.append(y_pos_mean, (np.mean(y_pos_data) - y_pos_first) * 1e3)  # record Y pos
        # x_pos_std = np.append(x_pos_std, abs(np.std(x_pos_data)))  # record X pos
        # y_pos_std = np.append(y_pos_std, abs(np.std(y_pos_data)))  # record Y pos


    # turn off the RF
    test_system_object.RF.turn_off_RF()

    data_out = {'test_name': test_name,
                'rf_id': test_system_object.rf_id,
                'bpm_id': test_system_object.bpm_id,
                'prog_atten_id': test_system_object.prog_atten_id,
                'frequency': frequency,
                'settling_time': settling_time,
                'set_output_power_levels': original_output_power_levels,
                'output_power_levels': applied_output_power_levels,
                'bpm_input_power': input_power,
                'bpm_agc': test_system_object.BPM.agc,
                'bpm_switching': test_system_object.BPM.switches,
                'bpm_dsc': test_system_object.BPM.dsc,
                'x_pos_raw': x_pos_raw,
                'y_pos_raw': y_pos_raw,
                'x_pos_raw_time': x_pos_raw_time,
                'y_pos_raw_time': y_pos_raw_time,
                'x_time_baseline': x_time_baseline,
                'x_pos_baseline': x_pos_baseline,
                'y_time_baseline': y_time_baseline,
                'y_pos_baseline': y_pos_baseline
                }

    # data_out = {'bpm_input_power': input_power,
    #             'x_pos_raw': list(x_pos_raw),
    #             'x_pos_mean': list(x_pos_mean),
    #             'x_pos_std': list(x_pos_std),
    #             'y_pos_raw': list(y_pos_raw),
    #             'y_pos_mean': list(y_pos_mean),
    #             'y_pos_std': list(y_pos_std),
    #             'bpm_agc': test_system_object.BPM.agc,
    #             'bpm_switching': test_system_object.BPM.switches,
    #             'bpm_dsc': test_system_object.BPM.dsc,
    #             'test_name': test_name,
    #             'rf_id': test_system_object.rf_id,
    #             'bpm_id': test_system_object.bpm_id,
    #             'prog_atten_id': test_system_object.prog_atten_id,
    #             'settling_time': settling_time,
    #             'frequency': frequency,
    #             'set_output_power_levels': original_output_power_levels,
    #             'output_power_levels': applied_output_power_levels}

    with open(sub_directory + "beam_power_dependence_data.json", 'w') as write_file:
        json.dump(data_out, write_file)
