import numpy as np
import time
from math import floor
import json
import helper_functions


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, complex):
            return [obj.real, obj.imag]
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def noise_test(test_system_object,
               frequency,
               samples=1000,
               output_power_levels=range(-20, -50, -5),
               settling_time=1,
               sub_directory=""):
    """Compares the noise generated.

    The RF signal is turned off, and then different parameters are measured from the BPM. 

    Args:
        test_system_object (System Obj): Object capturing the devices used, system losses and hardware ids.
        frequency (float): Output frequency for the tests, set as a float that will use the assumed units of MHz.
        samples (int): Number of sample to capture.
        output_power_levels (list): Output power for the tests, default value is np.arange(-100, 0, 10).
            The input values are floats and dBm is assumed.
        settling_time (float): Time in seconds, that the program will wait in between 
            setting an  output power on the RF, and reading the values of the BPM. 
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
        float array: X Positions read from the BPM
        float array: Y Positions read from the BPM
    """
    test_name = test_system_object.test_initialisation(test_name=__name__,
                                                       frequency=frequency,
                                                       output_power_level=output_power_levels[0])

    test_system_object.RF.turn_on_RF()

    # Perform the test
    x_time_baseline, x_pos_baseline = test_system_object.BPM.get_x_sa_data(samples)  # record X pos
    y_time_baseline, y_pos_baseline = test_system_object.BPM.get_y_sa_data(samples)  # record Y pos

    x_baseline_mean = np.mean(x_pos_baseline)
    y_baseline_mean = np.mean(y_pos_baseline)
    input_power = []
    output_power = []
    x_time = []
    x_pos = []
    y_time = []
    y_pos = []
    x_mean = []
    y_mean = []
    graph_legend = []
    bpm_input_power = []
    #  Gradually reducing the power level
    starting_attenuations = test_system_object.ProgAtten.get_global_attenuation()
    if starting_attenuations[0] - starting_attenuations[1] > 0.00001 or \
       starting_attenuations[0] - starting_attenuations[2] > 0.00001 or \
       starting_attenuations[0] - starting_attenuations[3] > 0.00001:
        raise ValueError('The initial attenuation values are not the same value')

    for index in output_power_levels:
        # Set attenuator value to give desired power level.
        test_system_object.ProgAtten.set_global_attenuation(starting_attenuations[0] + (output_power_levels[0] - index))
        time.sleep(settling_time)  # Wait for signal to settle
        bpm_input_power.append(test_system_object.BPM.get_input_power())
        x_time_tmp, x_pos_tmp = test_system_object.BPM.get_x_sa_data(samples)  # record X pos
        y_time_tmp, y_pos_tmp = test_system_object.BPM.get_y_sa_data(samples)  # record Y pos
        x_time.append(x_time_tmp)
        x_pos.append(x_pos_tmp)
        y_time.append(y_time_tmp)
        y_pos.append(y_pos_tmp)
        x_mean.append(np.mean(x_pos_tmp))
        y_mean.append(np.mean(y_pos_tmp))
        output_power.append(index)
        input_power.append(test_system_object.BPM.get_input_power())
        graph_legend.append(str(helper_functions.round_to_2sf(index)))

    # turn off the RF
        test_system_object.RF.turn_off_RF()

    specs = test_system_object.BPM.get_performance_spec()

    # Adding baseline data
    x_time.append(x_time_baseline)
    x_pos.append(x_pos_baseline)
    y_time.append(y_time_baseline)
    y_pos.append(y_pos_baseline)
    output_power.append(-100)  # Assuming -100 dBm is equivalent to off.
    bpm_input_power.append(-100)
    x_mean.append(x_baseline_mean)
    y_mean.append(y_baseline_mean)
    graph_legend.append('Baseline')
    # Change to frequency domain
    x_f_freq = []
    x_f_data = []
    y_f_freq = []
    y_f_data = []
    for inds in range(len(x_time)):
        x_f_freq_tmp, x_f_data_tmp = helper_functions.change_to_freq_domain(x_time[inds], x_pos[inds])
        y_f_freq_tmp, y_f_data_tmp = helper_functions.change_to_freq_domain(y_time[inds], y_pos[inds])
        upper_lim_x = int(floor(len(x_f_freq_tmp) / 2.))
        upper_lim_y = int(floor(len(y_f_freq_tmp) / 2.))
        # Starting at one to knock out DC value which messes up the scaling of the graph.
        x_f_freq.append(x_f_freq_tmp[1:upper_lim_x])
        x_f_data.append(x_f_data_tmp[1:upper_lim_x])
        y_f_freq.append(y_f_freq_tmp[1:upper_lim_y])
        y_f_data.append(y_f_data_tmp[1:upper_lim_y])

    data_out = {'n_bits': test_system_object.BPM.adc_n_bits,
                'n_adc': test_system_object.BPM.num_adcs,
                'bpm_agc': test_system_object.BPM.agc,
                'bpm_switching': test_system_object.BPM.switches,
                'bpm_dsc': test_system_object.BPM.dsc,
                'test_name': test_name,
                'rf_id': test_system_object.rf_id,
                'bpm_id': test_system_object.bpm_id,
                'prog_atten_id': test_system_object.prog_atten_id,
                'output_power': output_power,
                'output_power_levels': output_power_levels,
                'bpm_input_power': bpm_input_power,
                'x_time': x_time,
                'x_pos': x_pos,
                'y_time': y_time,
                'y_pos': y_pos,
                'x_mean': x_mean,
                'y_mean': y_mean,
                'graph_legend': graph_legend}

    data_out_complex = {'x_f_freq': x_f_freq,
                        'x_f_data': x_f_data,
                        'y_f_freq': y_f_freq,
                        'y_f_data': y_f_data,
                        }

    with open(sub_directory + "Noise_test_data.json", 'w') as write_file:
        json.dump(data_out, write_file)

    with open(sub_directory + "Noise_test_data_complex.json", 'w') as write_file_complex:
        json.dump(data_out_complex, write_file_complex, cls=ComplexEncoder)

