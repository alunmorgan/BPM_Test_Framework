from math import sqrt
import numpy as np
import helper_functions


def internal_attenuator_pass_fail(loaded_data, lim=0.1):
    # pass/fail test for internal attenuation
    data_test = list()
    print loaded_data['test_name']
    data = loaded_data['data']
    data_a = [np.mean(data[0]['sa_a_data'])]
    data_b = [np.mean(data[0]['sa_b_data'])]
    data_c = [np.mean(data[0]['sa_c_data'])]
    data_d = [np.mean(data[0]['sa_d_data'])]
    ref_a = np.mean(data[0]['sa_a_data'])
    ref_b = np.mean(data[0]['sa_b_data'])
    ref_c = np.mean(data[0]['sa_c_data'])
    ref_d = np.mean(data[0]['sa_d_data'])
    data_a_norm = [1]
    data_b_norm = [1]
    data_c_norm = [1]
    data_d_norm = [1]
    for atten_steps in range(1, len(data)):
        data_a.append(np.mean(data[atten_steps]['sa_a_data']))
        data_b.append(np.mean(data[atten_steps]['sa_b_data']))
        data_c.append(np.mean(data[atten_steps]['sa_c_data']))
        data_d.append(np.mean(data[atten_steps]['sa_d_data']))
        data_a_norm.append(data_a[atten_steps] / ref_a)
        data_b_norm.append(data_b[atten_steps] / ref_b)
        data_c_norm.append(data_c[atten_steps] / ref_c)
        data_d_norm.append(data_d[atten_steps] / ref_d)
    data_test.append(all([1 - lim < tmp < 1 + lim for tmp in data_a_norm]))
    data_test.append(all([1 - lim < tmp < 1 + lim for tmp in data_b_norm]))
    data_test.append(all([1 - lim < tmp < 1 + lim for tmp in data_c_norm]))
    data_test.append(all([1 - lim < tmp < 1 + lim for tmp in data_d_norm]))

    if all(data_test):
        print 'pass'
        return 'pass', True
    else:
        print 'fail'
        return 'fail', False


def power_dependence_pass_fail(loaded_data, level=100):
    # pass fail test for beam power dependence
    print loaded_data['test_name']
    if max(x_pos_mean_scaled_abs) < level and max(y_pos_mean_scaled_abs) < level:
        print 'pass'
        return 'pass', True
    else:
        print 'fail'
        return 'fail', False


def adc_bit_test_pass_fail(loaded_data, lim=0.05):
    # pass fail test for bit test
    print loaded_data['test_name']
    data_test = list()
    for kw in range(loaded_data['n_adc']):
        data_std = helper_functions.adc_missing_bit_analysis(loaded_data['data'][kw], loaded_data['n_bits'])
        data_test.append(all([0.5 - lim < tmp < 0.5 + lim for tmp in data_std]))

    if all(data_test):
        print 'pass'
        return 'pass', True
    else:
        print 'fail'
        return 'fail', False


def raster_scan_pass_fail(loaded_data, lim=0.02):
    # pass/fail test raster scan
    # Calculate predicted locations
    x_predicted = []
    y_predicted = []
    for inds in range(len(loaded_data['a_atten_readback'])):
        a, b, c, d = helper_functions.convert_attenuation_settings_to_abcd(loaded_data['starting_attenuations'],
                                                                           loaded_data['map_atten_bpm'],
                                                                           loaded_data['a_atten_readback'][inds],
                                                                           loaded_data['b_atten_readback'][inds],
                                                                           loaded_data['c_atten_readback'][inds],
                                                                           loaded_data['d_atten_readback'][inds])

        x_predicted.append(helper_functions.calc_x_pos(a, b, c, d, kx=1))
        y_predicted.append(helper_functions.calc_y_pos(a, b, c, d, ky=1))

    dists = list()
    for ne in range(len(x_predicted)):
        dists.append(sqrt((loaded_data['measured_x'][ne] - x_predicted[ne]) **2 +
                          (loaded_data['measured_y'][ne] - y_predicted[ne]) **2))
    print loaded_data['test_name']

    data_test = all([tmp < lim for tmp in dists])
    if data_test:
        print 'pass'
        return 'pass', True
    else:
        print 'fail'
        return 'fail', False
