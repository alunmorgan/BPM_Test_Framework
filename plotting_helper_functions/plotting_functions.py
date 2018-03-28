import matplotlib.pyplot as plt
from scipy.io import loadmat
import numpy as np


def line_plot_data(datasets, report_object, sub_directory):
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

    if report_object is None:
        # If no report is entered as an input to the test, simply display the results
        plt.show()
    else:
        plt.savefig(''.join((sub_directory, datasets[0][1][2])))
        report_object.add_figure_to_test(image_name=''.join((sub_directory, datasets[0][1][2])),
                                         caption=datasets[0][1][2])

    plt.cla()  # Clear axis
    plt.clf()  # Clear figure


def plot_adc_bit_check_data(report_object, sub_directory, input_file):
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    loaded_data = loadmat(''.join((sub_directory, input_file)))
    for kw in range(loaded_data['n_adc'][0][0]):
        format_plot.append(((np.arange(1, 16 + 1), loaded_data['data_std'][:, kw]),
                            ('bit number', 'Standard deviation', ' '.join(('ADC', str(kw + 1))),
                             'ADC_bit_check.pdf')))
    format_plot.append(((loaded_data['time'][0], loaded_data['data_adc1'][0]),
                        ('time', 'Data', 'ADC 1',
                         'ADC_data.pdf')))

    # plot all of the graphs
    cols = ['k', 'r', 'g', 'b']
    x_shift = 0
    cols_ind = 0
    for index in format_plot[:-1]:
        plt.bar(index[0][0] + x_shift, index[0][1], align='center', width=0.15, label=index[1][2], color=cols[cols_ind])
        x_shift = x_shift + 0.1
        cols_ind = cols_ind + 1
    plt.legend(loc='upper right')
    plt.xlabel(format_plot[0][1][0])
    plt.ylabel(format_plot[0][1][1])
    plt.xlim(0.5, loaded_data['n_bits'][0][0] + 1)
    plt.ylim(0, 1)

    if report_object is None:
        # If no report is entered as an input to the test, simply display the results
        plt.show()
    else:
        plt.savefig(''.join((sub_directory, format_plot[0][1][3])))
        report_object.add_figure_to_test(image_name=''.join((sub_directory, format_plot[0][1][3])),
                                         caption='ADC bit test. All should be close to 0.5')
    plt.cla()  # Clear axis
    plt.clf()  # Clear figure

    plt.plot(format_plot[-1][0][0], format_plot[-1][0][1], label=format_plot[-1][1][2])
    plt.legend(loc='upper right')
    plt.xlabel(format_plot[-1][1][0])
    plt.ylabel(format_plot[-1][1][1])

    if report_object is None:
        # If no report is entered as an input to the test, simply display the results
        plt.show()
    else:
        plt.savefig(''.join((sub_directory, format_plot[-1][1][3])))
        report_object.add_figure_to_test(image_name=''.join((sub_directory, format_plot[-1][1][3])),
                                         caption='ADC bit test. All should be close to 0.5')
    plt.cla()  # Clear axis
    plt.clf()  # Clear figure


def plot_adc_int_atten_sweep_data(report_object, sub_directory, input_file):
    # Get the plot values in a format that is easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    loaded_data = loadmat(''.join((sub_directory, input_file)))
    for hw in range(loaded_data['n_adc'][0][0]):
        format_plot.append(((loaded_data['attenuation'][0],
                             loaded_data['data_corrected'][:, hw],
                             loaded_data['data_std'][:, hw]),
                            ('attenuation', 'counts',
                             "ADC_varying_internal_attenuation.pdf", ' '.join(('ADC', str(hw))))))

    # plot all of the graphs
    line_plot_data([format_plot[0], format_plot[1], format_plot[2], format_plot[3]], report_object, sub_directory)


def plot_beam_power_dependence_data(report_object, sub_directory, input_file):
    # Get the plot values in a format that's easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    loaded_data = loadmat(''.join((sub_directory, input_file)))
    format_plot.append(((loaded_data['power_levels'][0], loaded_data['input_power'][0]),
                        ('RF Source Power Output (dBm)',
                         'Power input at BPM (dBm)',
                         "power_vs_power.pdf")))
    format_plot.append(((loaded_data['power_levels'][0], abs(loaded_data['x_pos_mean'][0]), loaded_data['x_pos_std']),
                        ('RF Source Power Output (dBm)',
                         'Beam Position (um)',
                         "power_vs_position_spec.pdf",
                         'Horizontal')))
                        #  loaded_data['bpm_specs']['Beam_power_dependence_X']))
    format_plot.append(((loaded_data['power_levels'][0], abs(loaded_data['y_pos_mean'][0]), loaded_data['y_pos_std']),
                        ('RF Source Power Output (dBm)',
                         'Beam Position (um)',
                         "power_vs_position_spec.pdf",
                         'Vertical')))
                        #  loaded_data['bpm_specs']['Beam_power_dependence_Y']))
    format_plot.append(((loaded_data['power_levels'], loaded_data['x_pos_mean'][0], loaded_data['x_pos_std']),
                        ('RF Source Power Output (dBm)',
                         'Beam Position (um)',
                         "power_vs_position.pdf",
                         'Horizontal')))
    format_plot.append(((loaded_data['power_levels'], loaded_data['y_pos_mean'][0], loaded_data['y_pos_std']),
                        ('RF Source Power Output (dBm)',
                         'Beam Position (um)',
                         "power_vs_position.pdf",
                         'Vertical')))

    line_plot_data([format_plot[0]], report_object, sub_directory)
    line_plot_data([format_plot[1], format_plot[2]], report_object, sub_directory)
    line_plot_data([format_plot[3], format_plot[4]], report_object, sub_directory)


def plot_scaled_voltage_amplitude_fill_pattern_data(report_object, sub_directory, input_file):
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    loaded_data = loadmat(''.join((sub_directory, input_file)))
    format_plot.append(((loaded_data['duty_cycles'], loaded_data['x_pos_mean'][0], loaded_data['x_pos_std'][0]),
                                     ('Gating signal duty cycle (0-1)',
                                     'Beam Position (um) (Normalised at 1)',
                                     "scaled_DC_vs_position.pdf", 'Horizontal',)))
    format_plot.append(((loaded_data['duty_cycles'], loaded_data['y_pos_mean'][0], loaded_data['y_pos_std'][0]),
                        ('(Gating signal duty cycle (0-1)',
                       'Beam Position (um) (Normalised at 1)'
                        "scaled_DC_vs_Y.pdf", 'Vertical')))

    line_plot_data([format_plot[0], format_plot[1]], report_object, sub_directory)


def plot_fixed_voltage_amplitude_fill_pattern_data(report_object, sub_directory, input_file):
    # Get the plot values in a format thats easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    loaded_data = loadmat(''.join((sub_directory, input_file)))
    format_plot.append(((loaded_data['duty_cycles'][0], loaded_data['x_pos_mean'][0], loaded_data['x_pos_std'][0]),
                        ('Gating signal duty cycle (0-1)', 'Beam Position (um) (Normalised at 1)',
                         "Duty_cycle_vs_position.pdf", 'Horizontal')))
    format_plot.append(((loaded_data['duty_cycles'][0], loaded_data['y_pos_mean'][0], loaded_data['y_pos_std'][0]),
                        ('Gating signal duty cycle (0-1)', 'Beam Position (um) (Normalised at 1)',
                         "Duty_cycle_vs_position.pdf", 'Vertical')))
    line_plot_data([format_plot[0], format_plot[1]], report_object, sub_directory)
