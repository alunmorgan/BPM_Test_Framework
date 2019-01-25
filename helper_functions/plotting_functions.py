import matplotlib.pyplot as plt
import numpy as np


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


def plot_adc_bit_check_data(sub_directory, loaded_data):
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    for kw in range(loaded_data['n_adc']):
        format_plot.append(((np.arange(1, loaded_data['n_bits'] + 1), loaded_data['data_std'][kw]),
                            ('bit number', 'Standard deviation', ' '.join(('ADC', str(kw + 1))),
                             'ADC_bit_check.pdf')))
        format_plot.append(((loaded_data['time'], loaded_data[''.join(('data_adc', str(kw + 1)))]),
                            ('time', 'Data', ' '.join(('ADC', str(kw + 1))),
                             'ADC_data.pdf')))

    # plot all of the graphs
    cols = ['k', 'r', 'g', 'b']
    x_shift = 0
    cols_ind = 0
    for index in format_plot[0::2]:
        plt.bar(index[0][0] + x_shift, index[0][1], align='center', width=0.15, label=index[1][2], color=cols[cols_ind])
        x_shift = x_shift + 0.1
        cols_ind = cols_ind + 1
    plt.legend(loc='upper right')
    plt.xlabel(format_plot[0][1][0])
    plt.ylabel(format_plot[0][1][1])
    plt.xlim(0.5, loaded_data['n_bits'] + 1)
    plt.ylim(0, 1)
    fig1_name = ''.join((sub_directory, format_plot[0][1][3]))
    plt.savefig(fig1_name)
    plt.cla()  # Clear axis
    plt.clf()  # Clear figure

    for index in format_plot[1::2]:
        plt.plot(index[0][0], index[0][1], label=index[1][2])
    plt.legend(loc='upper right')
    plt.xlabel(format_plot[1][1][0])
    plt.ylabel(format_plot[1][1][1])
    fig2_name = ''.join((sub_directory, format_plot[1][1][3]))
    plt.savefig(fig2_name)
    plt.cla()  # Clear axis
    plt.clf()  # Clear figure
    return fig1_name, fig2_name


def plot_adc_int_atten_sweep_data(sub_directory, loaded_data):
    # Get the plot values in a format that is easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    for nes in range(loaded_data['n_adc']):
        mean_temp = []
        std_temp = []
        for dda in range(len(loaded_data['data'])):
            mean_temp.append(loaded_data['data_mean'][dda][nes])
            std_temp.append(loaded_data['data_std'][dda][nes])
        format_plot.append(((loaded_data['output_power'], mean_temp, std_temp),
                            ('power', 'counts',
                             "ADC_varying_internal_attenuation.pdf", ' '.join(('ADC', str(nes + 1))))))

    # plot all of the graphs
    fig_name = line_plot_data([format_plot[0], format_plot[1], format_plot[2], format_plot[3]], sub_directory)
    return fig_name


def plot_beam_power_dependence_data(sub_directory, loaded_data):
    # Get the plot values in a format that's easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption

    # format_plot.append(((loaded_data['output_power_levels'], loaded_data['bpm_input_power']),
    #                     ('Test system Power Output (dBm)',
    #                      'Input power recorded by BPM (dBm)',
    #                      "power_vs_power.pdf")))

    format_plot.append(((loaded_data['output_power_levels'], loaded_data['x_pos_mean'], loaded_data['x_pos_std']),
                        ('Input power (dBm)',
                         'Beam Position (um)',
                         "power_vs_position.pdf",
                         'Horizontal')))
    format_plot.append(((loaded_data['output_power_levels'], loaded_data['y_pos_mean'], loaded_data['y_pos_std']),
                        ('Input power (dBm)',
                         'Beam Position (um)',
                         "power_vs_position.pdf",
                         'Vertical')))
    # format_plot.append(((loaded_data['power_levels'], loaded_data['x_pos_mean'], loaded_data['x_pos_std']),
    #                     ('RF Source Power Output (dBm)',
    #                      'Beam Position (um)',
    #                      "power_vs_position_spec.pdf",
    #                      'Horizontal')))
    #                     #  loaded_data['bpm_specs']['Beam_power_dependence_X']))
    # format_plot.append(((loaded_data['power_levels'], loaded_data['y_pos_mean'], loaded_data['y_pos_std']),
    #                     ('RF Source Power Output (dBm)',
    #                      'Beam Position (um)',
    #                      "power_vs_position_spec.pdf",
    #                      'Vertical')))
    #                     #  loaded_data['bpm_specs']['Beam_power_dependence_Y']))

    # fig1_name = line_plot_data([format_plot[0]], sub_directory)
    fig1_name = line_plot_data([format_plot[0], format_plot[1]], sub_directory)
    #  fig3_name = line_plot_data([format_plot[3], format_plot[4]], sub_directory)
    return fig1_name


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
    plt.plot(loaded_data['measured_x'], loaded_data['measured_y'], 'bo',
             loaded_data['predicted_x'], loaded_data['predicted_y'], 'r+', markersize=10, )
    plt.xlabel("Horizontal Beam Position (mm)")
    plt.ylabel("Vertical Beam Position (mm)")
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
    format_plot.append((([loaded_data['bpm_input_power'], loaded_data['bpm_input_power']],
                         [loaded_data['x_mean'], loaded_data['y_mean']]),
                        ('BPM input power (dBm)', 'mean values', "SA_means_at_different_power.pdf", ['x', 'y'])))
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
                    plt.plot(index[0][0][ks], index[0][1][ks])
        else:
            plt.plot(index[0][0], index[0][1])

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
