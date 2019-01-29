import numpy as np


def calc_x_pos(a, b, c, d, kx):
    diff = ((a+d)-(b+c))
    total = (a+b+c+d)
    x = kx*(diff/total)
    return x


def calc_y_pos(a, b, c, d, ky):
    diff = ((a+b)-(c+d))
    total = (a+b+c+d)
    y = ky*(diff/total)
    return y


def multiply_list(lst, multiple):
    output = []
    for val in lst:
        output.append(val * multiple)
    return output


def quarter_round(x):
    return round(x * 4) / 4


def convert_attenuation_settings_to_abcd(starting_attenuations, map_atten_bpm,
                                         a_atten_readback, b_atten_readback, c_atten_readback, d_atten_readback):
    a_applied_adj = starting_attenuations[map_atten_bpm['A'] - 1] - a_atten_readback
    b_applied_adj = starting_attenuations[map_atten_bpm['B'] - 1] - b_atten_readback
    c_applied_adj = starting_attenuations[map_atten_bpm['C'] - 1] - c_atten_readback
    d_applied_adj = starting_attenuations[map_atten_bpm['D'] - 1] - d_atten_readback
    a_applied = 0.25 * 10 ** a_applied_adj
    b_applied = 0.25 * 10 ** b_applied_adj
    c_applied = 0.25 * 10 ** c_applied_adj
    d_applied = 0.25 * 10 ** d_applied_adj
    

def round_to_2sf(input_vals):
    if type(input_vals) is list:
        output = []
        for num in input_vals:
            output.append(round(num * 100.) / 100.)
    else:
        output = round(input_vals * 100.) / 100.

    return output


def change_to_freq_domain(times, data):
    f_data = np.fft.fft(data)
    f_data_mag = []
    for f_sample in f_data:
        f_data_mag.append(abs(f_sample))

    sample_spacing = []
    for nd in range(len(times) - 2):
        sample_spacing.append(times[nd + 1] - times[nd])
    sample_spacing = np.mean(sample_spacing)
    f_freq = list(np.fft.fftfreq(len(times), sample_spacing))
    return f_freq, f_data_mag


def get_stats(data):
    data_mean = np.mean(data)
    data_std = np.std(data)
    data_max = max(data)
    data_min = min(data)
    return data_mean, data_std, data_max, data_min


def subtract_mean(data, mean_value):
    if data is list:
        output = []
        for val in data:
            output.append(val - mean_value)
    else:
        output = data - mean_value

    return output


def stat_dataset(dataset):
    mean_list = []
    std_list = []
    for single_set in dataset:
        mean_tmp, std_tmp, _2, _3 = get_stats(single_set)
        mean_list.append(mean_tmp)
        std_list.append(std_tmp)
    return mean_list, std_list


def reconfigure_adc_data(data):
    data_out = list()
    for num_adc in range(len(data[0])):
        data_out.append([])
    for repeat_point in range(len(data)):
        for num_adc in range(len(data[repeat_point])):
            data_out[num_adc].extend(data[repeat_point][num_adc])
    return data_out


def adc_missing_bit_analysis(data, n_bits):
    # First convert the int value into a binary string.
    # Turn that string into a list of values.
    # This should be bpm_object.adc_n_bits in size. However if this is not 16 there is a broadcast error.
    # This is because the epics layer always returns a 16 bit number.
    # For now set to 16. The upper extra bits will be ignored in the later processing anyway.
    format_string = '0%db' % 16  # bpm_object.adc_n_bits
    data_bits = [list(format(int(x), format_string)) for x in data]

    # Calculating the standard deviation of each bit location.
    data_bits_std = []
    # for kw in range(test_system_object.BPM.num_adcs):
    #     data_std.append([])
    for wn in range(n_bits):
        temp = []
        for en in range(len(data)):
            temp.append(int(data_bits[en][wn]))

        data_bits_std.append(np.std(temp))

    return data_bits_std
