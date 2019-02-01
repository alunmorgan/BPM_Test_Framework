import matplotlib.pyplot as plt
import numpy as np
import helper_functions.helper_calc_functions


def line_plot_data(datasets, sub_directory):
    for dt in range(len(datasets)):
        index = datasets[dt]
        if len(index[1]) == 4:
            lab = index[1][3]
        else:
            lab = ''
        if len(index[0]) == 2:
            plt.plot(index[0][0], index[0][1], label=lab)
        elif len(index[0]) == 3:
            plt.errorbar(index[0][0], index[0][1], index[0][2], label=lab)

    plt.xlabel(datasets[0][1][0])
    plt.ylabel(datasets[0][1][1])
    plt.legend(loc='upper right')
    plt.grid(True)
    if len(datasets[0]) == 3:
        # There is a specification line. Add this.
        # Spec is in um while data is in mm so scale by 1E-3.
        plt.plot(datasets[0][2][0], datasets[0][2][1], 'r')
    fig_name = ''.join((sub_directory, datasets[0][1][2]))
    plt.savefig(fig_name)
    plt.cla()  # Clear axis
    plt.clf()  # Clear figure
    return fig_name


def bar_plot_data(datasets, sub_directory):
    cols = ['k', 'r', 'g', 'b']
    x_shift = 0
    cols_ind = 0
    for index in datasets:
        plt.bar(index[0][0] + x_shift, index[0][1], align='center', width=0.15, label=index[1][3], color=cols[cols_ind])
        x_shift = x_shift + 0.1
        cols_ind = cols_ind + 1
    plt.legend(loc='upper right')
    plt.xlabel(datasets[0][1][0])
    plt.ylabel(datasets[0][1][1])
    x_step = datasets[0][0][0][1] - datasets[0][0][0][0]
    plt.xlim(datasets[0][0][0][0] - x_step / 2., datasets[0][0][0][-1] + x_step / 2.)
    plt.ylim(0, 1)
    fig_name = ''.join((sub_directory, datasets[0][1][2]))
    plt.savefig(fig_name)
    plt.cla()  # Clear axis
    plt.clf()  # Clear figure
    return fig_name


def plot_adc_bit_check_data(sub_directory, loaded_data):
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    data = loaded_data['data']
    for kw in range(loaded_data['n_adc']):
        data_std = helper_functions.adc_missing_bit_analysis(data[kw], loaded_data['n_bits'])
        format_plot.append(((np.arange(1, loaded_data['n_bits'] + 1), data_std),
                            ('bit number', 'Standard deviation', 'ADC_bit_check.pdf', ' '.join(('ADC', str(kw + 1))))))
        # format_plot.append(((loaded_data['time'], data[kw]),
        #                     ('time', 'Data', 'ADC_data.pdf', ' '.join(('ADC', str(kw + 1))))))

    fig1_name = bar_plot_data(format_plot, sub_directory)
    # fig2_name = line_plot_data(format_plot[1::2], sub_directory)
    return fig1_name#, fig2_name


def plot_adc_int_atten_sweep_data(sub_directory, loaded_data):
    # Get the plot values in a format that is easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    data = loaded_data['data']
    adc_mean = list()
    adc_std = list()
    for atten_steps in range(len(data)):
        data_temp = helper_functions.reconfigure_adc_data(data[atten_steps])
        if atten_steps == 0:
            for adc in range(len(data_temp)):
                adc_mean.append([])
                # adc_std.append([])
        for adc in range(len(data_temp)):
            adc_mean[adc].append(np.mean(data_temp[adc]))
            # adc_std[adc].append(np.std(data_temp[adc]))

    for adc_num in range(len(adc_mean)):
        format_plot.append(((loaded_data['output_power'], adc_mean[adc_num]),
                            ('power', 'counts',
                             "ADC_varying_internal_attenuation.pdf", ' '.join(('ADC', str(adc_num + 1))))))

    # plot all of the graphs
    fig_name = line_plot_data([format_plot[0], format_plot[1], format_plot[2], format_plot[3]], sub_directory)
    return fig_name


def plot_beam_power_dependence_data(sub_directory, loaded_data):
    # Get the plot values in a format that's easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption

    x_pos_mean, x_pos_std = helper_functions.helper_calc_functions.stat_dataset(loaded_data['x_pos_raw'])
    y_pos_mean, y_pos_std = helper_functions.helper_calc_functions.stat_dataset(loaded_data['y_pos_raw'])
    x_noise_freq, x_noise_fft = helper_functions.helper_calc_functions.change_to_freq_domain(
        loaded_data['x_time_baseline'], loaded_data['x_pos_baseline'])
    y_noise_freq, y_noise_fft = helper_functions.helper_calc_functions.change_to_freq_domain(
        loaded_data['y_time_baseline'], loaded_data['y_pos_baseline'])
    print y_noise_freq

    format_plot.append(((loaded_data['output_power_levels'], x_pos_mean, x_pos_std),
                        ('Input power (dBm)', 'Beam Position (um)', "power_vs_position.pdf", 'Horizontal')))
    format_plot.append(((loaded_data['output_power_levels'], y_pos_mean, y_pos_std),
                        ('Input power (dBm)', 'Beam Position (um)', "power_vs_position.pdf", 'Vertical')))
    format_plot.append(((loaded_data['x_time_baseline'], loaded_data['x_pos_baseline']),
                        ('Time (s)', 'Position (um)', "baseline_noise_time.pdf", 'Horizontal')))
    format_plot.append(((loaded_data['y_time_baseline'], loaded_data['y_pos_baseline']),
                        ('Time (s)', 'Position (um)', "baseline_noise_time.pdf", 'Vertical')))
    format_plot.append(((x_noise_freq[1:int(len(x_noise_freq)/2.)], x_noise_fft[1:int(len(x_noise_freq)/2.)]),
                        ('Frequency ()', 'Position (um)', "baseline_noise_frequency.pdf", 'Horizontal')))
    format_plot.append(((y_noise_freq[1:int(len(y_noise_freq)/2.)], y_noise_fft[1:int(len(y_noise_freq)/2.)]),
                        ('Frequency ()', 'Position (um)', "baseline_noise_frequency.pdf", 'Vertical')))
    format_plot.append(((loaded_data['bpm_specs']['Beam_current_dependence_X'][0],
                         loaded_data['bpm_specs']['Beam_current_dependence_X'][1]),
                        ('Input power (dBm)', 'Beam Position (um)', "power_vs_position.pdf", 'Horizontal')))
    format_plot.append(((loaded_data['bpm_specs']['Beam_current_dependence_Y'][0],
                         loaded_data['bpm_specs']['Beam_current_dependence_Y'][1]),
                        ('Input power (dBm)', 'Beam Position (um)', "power_vs_position.pdf", 'Vertical')))

    # fig1_name = line_plot_data([format_plot[0]], sub_directory)
    fig1_name = line_plot_data([format_plot[0], format_plot[1], format_plot[6], format_plot[7]], sub_directory)
    fig2_name = line_plot_data([format_plot[2], format_plot[3]], sub_directory)
    fig3_name = line_plot_data([format_plot[4], format_plot[5]], sub_directory)
    return fig1_name, fig2_name, fig3_name


def plot_scaled_voltage_amplitude_fill_pattern_data(sub_directory, loaded_data):
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    format_plot.append(((loaded_data['duty_cycles'][0], loaded_data['x_pos_mean'][0], loaded_data['x_pos_std'][0]),
                                     ('Gating signal duty cycle (0-1)',
                                      'Beam Position (um) (Normalised at 1)',
                                      "scaled_DC_vs_position.pdf", 'Horizontal',)))
    format_plot.append(((loaded_data['duty_cycles'][0], loaded_data['y_pos_mean'][0], loaded_data['y_pos_std'][0]),
                        ('(Gating signal duty cycle (0-1)',
                       'Beam Position (um) (Normalised at 1)'
                        "scaled_DC_vs_Y.pdf", 'Vertical')))

    fig_name = line_plot_data([format_plot[0], format_plot[1]], sub_directory)
    return fig_name


def plot_fixed_voltage_amplitude_fill_pattern_data(sub_directory, loaded_data):
    # Get the plot values in a format thats easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    format_plot.append(((loaded_data['duty_cycles'][0], loaded_data['x_pos_mean'][0], loaded_data['x_pos_std'][0]),
                        ('Gating signal duty cycle (0-1)', 'Beam Position (um) (Normalised at 1)',
                         "Duty_cycle_vs_position.pdf", 'Horizontal')))
    format_plot.append(((loaded_data['duty_cycles'][0], loaded_data['y_pos_mean'][0], loaded_data['y_pos_std'][0]),
                        ('Gating signal duty cycle (0-1)', 'Beam Position (um) (Normalised at 1)',
                         "Duty_cycle_vs_position.pdf", 'Vertical')))
    fig_name = line_plot_data([format_plot[0], format_plot[1]], sub_directory)
    return fig_name


def plot_raster_scan(sub_directory, loaded_data):
    x_predicted = []
    y_predicted = []
    for inds in range(len(loaded_data['a_atten_readback'])):
        a, b, c, d = helper_functions.convert_attenuation_settings_to_abcd(loaded_data['starting_attenuations'],
                                                                           loaded_data['map_atten_bpm'],
                                             loaded_data['a_atten_readback'][inds], loaded_data['b_atten_readback'][inds],
                                             loaded_data['c_atten_readback'][inds], loaded_data['d_atten_readback'][inds])

        x_predicted.append(helper_functions.calc_x_pos(a, b, c, d, kx=1))
        y_predicted.append(helper_functions.calc_y_pos(a, b, c, d, ky=1))

    plt.plot(helper_functions.multiply_list(helper_functions.add_list(loaded_data['measured_x'], 0.), 1),
             helper_functions.multiply_list(loaded_data['measured_y'], 1), 'bo',
             loaded_data['requested_x'], loaded_data['requested_y'], 'r+',
             helper_functions.multiply_list(x_predicted, 1),
             helper_functions.multiply_list(y_predicted, 1), 'g+',
             markersize=10)
    plt.xlabel("Horizontal Beam Position (mm)")
    plt.ylabel("Vertical Beam Position (mm)")
    plt.legend(('Measured', 'Requested', 'Predicted'),loc='upper right')
    plt.grid(True)
    fig_name = ''.join((sub_directory, "Beam_position_equidistant_grid_raster_scan_test" + ".pdf"))
    plt.savefig(fig_name)
    return fig_name


def plot_noise(sub_directory, loaded_data, loaded_data_complex):

    # Get the plot values in a format that is easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption

    format_plot.append(((loaded_data['x_time'], loaded_data['x_pos']),
                        ('Time (s)', 'Horizontal Beam Position (mm)', "SA_at_different_power_x.pdf",
                         loaded_data['graph_legend'])))
    format_plot.append(((loaded_data['y_time'], loaded_data['y_pos']),
                        ('Time (s)', 'Vertical Beam Position (mm)', "SA_at_different_power_y.pdf",
                         loaded_data['graph_legend'])))
    format_plot.append((([loaded_data['output_power'], loaded_data['output_power']],
                         [loaded_data['x_mean'], loaded_data['y_mean']]),
                        ('Power at BPM input (dBm)', 'mean values', "SA_means_at_different_power.pdf", ['x', 'y'])))
    format_plot.append(((loaded_data_complex['x_f_freq'], loaded_data_complex['x_f_data']),
                        ('Frequency (Hz)', 'Horizontal Beam Position', "Baseline_noise_spectrum_x.pdf",
                         loaded_data['graph_legend'])))
    format_plot.append(((loaded_data_complex['y_f_freq'], loaded_data_complex['y_f_data']),
                        ('Frequency (Hz)', 'Vertical Beam Position', "Baseline_noise_spectrum_y.pdf",
                         loaded_data['graph_legend'])))

    fig_names = []
    for index in format_plot:
        if type(index[0][0][0]) is list:
            for ks in range(len(index[0][0])):
                if len(index[1]) == 4:
                    plt.plot(index[0][0][ks], index[0][1][ks], label=index[1][3][ks])
                else:
                    plt.plot(index[0][0][ks], index[0][1][ks], 's')
        else:
            plt.plot(index[0][0], index[0][1], 's')

        plt.xlabel(index[1][0])
        plt.ylabel(index[1][1])
        plt.legend()
        plt.grid(True)
        if len(index) == 3:
            # There is a specification line. Add this.
            plt.plot(index[2][0], index[2][1], 'r')

        fig_names.append(''.join((sub_directory, index[1][2])))
        plt.savefig(fig_names[-1])

        plt.cla()  # Clear axis
        plt.clf()  # Clear figure

    return fig_names
