from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
import numpy as np
import matplotlib.pyplot as plt
import time
from math import floor


def change_to_freq_domain(times, data):
    f_data = np.fft.fft(data)
    sample_spacing = []
    for nd in range(len(times) - 2):
        sample_spacing.append(times[nd + 1] - times[nd])
    sample_spacing = np.mean(sample_spacing)
    f_freq = np.fft.fftfreq(len(times), sample_spacing)
    return list(f_freq), list(f_data)


def noise_test(rf_object,
               bpm_object,
               prog_atten_object,
               frequency,
               samples=1000,
               power_levels=np.arange(-20, -50, -5),
               settling_time=1,
               report_object=None,
               sub_directory=""):
    """Compares the noise generated.

    The RF signal is turned off, and then different parameters are measured from the BPM. 

    Args:
        rf_object (RFSignalGenerator Obj): Object to interface with the RF hardware.
        bpm_object (BPMDevice Obj): Object to interface with the BPM hardware.
        samples (int): The number of samples in each aquisition.
        prog_atten_object (Prog_Atten Obj): Object to interface with programmable attenuator hardware.
        frequency (float): Output frequency for the tests, set as a float that will use the assumed units of MHz.
        power_levels (list): Output power for the tests, default value is np.arange(-100, 0, 10).
            The input values are floats and dBm is assumed.
        settling_time (float): Time in seconds, that the program will wait in between 
            setting an  output power on the RF, and reading the values of the BPM. 
        report_object (LaTeX Report Obj): Specific report that the test results will be recorded 
            to. If no report is sent to the test then it will just display the results in a graph. 
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
        float array: X Positions read from the BPM
        float array: Y Positions read from the BPM
    """

    # Formats the test name and tells the user the test has started
    test_name = __name__
    test_name = test_name.rsplit("Tests.")[1]
    test_name = test_name.replace("_", " ")
    print("Starting test \"" + test_name + "\"")

    # Set the initial state of the RF device
    rf_object.turn_off_RF()
    rf_object.set_frequency(frequency)
    # Forcing to be an int as decimal points will cause the command sent to fail
    rf_object.set_output_power(int(power_levels[0]))
    prog_atten_object.set_global_attenuation(0)
    rf_object.turn_on_RF()

    # Perform the test
    x_time_baseline, x_pos_baseline = bpm_object.get_x_sa_data(samples)  # record X pos
    y_time_baseline, y_pos_baseline = bpm_object.get_y_sa_data(samples)  # record Y pos

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
    #  Gradually reducing the power level
    for index in power_levels:
        # Set attenuator value to give desired power level.
        prog_atten_object.set_global_attenuation(power_levels[0] - index)
        time.sleep(settling_time)  # Wait for signal to settle
        x_time_tmp, x_pos_tmp = bpm_object.get_x_sa_data(samples)  # record X pos
        y_time_tmp, y_pos_tmp = bpm_object.get_y_sa_data(samples)  # record Y pos
        x_time.append(x_time_tmp)
        x_pos.append(x_pos_tmp)
        y_time.append(y_time_tmp)
        y_pos.append(y_pos_tmp)
        x_mean.append(np.mean(x_pos_tmp))
        y_mean.append(np.mean(y_pos_tmp))
        output_power.append(index)
        input_power.append(bpm_object.get_input_power())
        graph_legend.append(str(index))

    # turn off the RF
    rf_object.turn_off_RF()

    specs = bpm_object.get_performance_spec()

    # Adding baseline data
    x_time.append(x_time_baseline)
    x_pos.append(x_pos_baseline)
    y_time.append(y_time_baseline)
    y_pos.append(y_pos_baseline)
    output_power.append(-100)  # Assuming -100 dBm is equivalent to off.
    x_mean.append(x_baseline_mean)
    y_mean.append(y_baseline_mean)
    graph_legend.append('Baseline')
    print 'Starting freq conversions'
    # Change to frequency domain
    x_f_freq = []
    x_f_data = []
    y_f_freq = []
    y_f_data = []
    for inds in range(len(x_time)):
        x_f_freq_tmp, x_f_data_tmp = change_to_freq_domain(x_time[inds], x_pos[inds])
        y_f_freq_tmp, y_f_data_tmp = change_to_freq_domain(y_time[inds], y_pos[inds])
        upper_lim_x = int(floor(len(x_f_freq_tmp) / 2.))
        upper_lim_y = int(floor(len(y_f_freq_tmp) / 2.))
        # Starting at one to knock out DC value which messes up the scaling of the graph.
        x_f_freq.append(x_f_freq_tmp[1:upper_lim_x])
        x_f_data.append(x_f_data_tmp[1:upper_lim_x])
        y_f_freq.append(y_f_freq_tmp[1:upper_lim_y])
        y_f_data.append(y_f_data_tmp[1:upper_lim_y])
    print 'Freq conversions done'
    # Get the plot values in a format that is easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption

    format_plot.append(((x_time, x_pos),
                       ('Time (s)', 'Horizontal Beam Position (mm)', "SA_at_different_power_x.pdf", graph_legend)))
    format_plot.append(((y_time, y_pos),
                       ('Time (s)', 'Vertical Beam Position (mm)', "SA_at_different_power_y.pdf", graph_legend)))
    format_plot.append((([output_power, output_power], [x_mean, y_mean]),
                       ('Output power (dBm)', 'mean values', "SA_means_at_different_power.pdf", ['x', 'y'])))
    format_plot.append(((x_f_freq, x_f_data),
                       ('Frequency (Hz)', 'Horizontal Beam Position', "Baseline_noise_spectrum_x.pdf", graph_legend)))
    format_plot.append(((y_f_freq, y_f_data),
                       ('Frequency (Hz)', 'Vertical Beam Position', "Baseline_noise_spectrum_y.pdf", graph_legend)))

    if report_object is not None:
        intro_text = r"""Compares the noise generated.

            The RF signal is turned off, and then different parameters are measured from the BPM.  \\~\\
            """
        # Get the device names for the report
        device_names = []
        device_names.append('RF source is ' + rf_object.get_device_id())
        device_names.append('BPM is ' + bpm_object.get_device_id())
        # Get the parameter values for the report
        parameter_names = []
        parameter_names.append("power levels: " + str(power_levels))
        # add the test details to the report
        report_object.setup_test(test_name, intro_text, device_names, parameter_names)
        # make a caption and headings for a table of results
        #caption = "Noise Results"
        #headings = [["X Position", "Y Position", ], ["(mm)", "(mm)"]]
        #data = [x_pos_baseline, y_pos_baseline]
        # copy the values to the report
        #report_object.add_table_to_test('|c|c|', data, headings, caption)

    # plot all of the graphs
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
        if report_object is None:
            # If no report is entered as an input to the test, simply display the results
            plt.show()
        else:
            plt.savefig(''.join((sub_directory, index[1][2])))
            report_object.add_figure_to_test(image_name=''.join((sub_directory, index[1][2])), caption=index[1][2])

        plt.cla()  # Clear axis
        plt.clf()  # Clear figure
    # return the full data sets
    return x_time, x_pos, y_time, y_pos
