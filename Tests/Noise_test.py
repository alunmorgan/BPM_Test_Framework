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
    return f_freq, f_data


def noise_test(rf_object,
               bpm_object,
               frequency,
               start_power=-100,
               end_power=0,
               samples=10,
               settling_time=1,
               report_object=None,
               sub_directory=""):
    """Compares the noise generated.

    The RF signal is turned off, and then different parameters are measured from the BPM. 

    Args:
        rf_object (RFSignalGenerator Obj): Object to interface with the RF hardware.
        bpm_object (BPMDevice Obj): Object to interface with the BPM hardware.

        frequency (float): Output frequency for the tests, set as a float that will use the assumed units of MHz. 
        start_power (float): Starting output power for the tests, default value is -100 dBm. 
            The input values are floats and dBm is assumed. 
        end_power (float): Final output power for the tests, default value is 0 dBm.
            The input values are floats and dBm assumed. 
        samples (int): Number of samples take.
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

    # Perform the test
    x_time_baseline, x_pos_baseline = bpm_object.get_x_sa_data(samples)  # record X pos
    y_time_baseline, y_pos_baseline = bpm_object.get_y_sa_data(samples)  # record Y pos
    x_f_freq_baseline, x_f_data_baseline = change_to_freq_domain(x_time_baseline, x_pos_baseline)
    y_f_freq_baseline, y_f_data_baseline = change_to_freq_domain(y_time_baseline, y_pos_baseline)

    power = np.linspace(start_power, end_power, samples)  # Creates samples to test
    rf_object.set_frequency(frequency)
    rf_object.set_output_power(start_power)
    rf_object.turn_on_RF()
    x_time = []
    x_pos = []
    y_time = []
    y_pos = []
    output_power = []
    input_power = []
    for index in power:
        rf_object.set_output_power(index)  # Set next output power value
        time.sleep(settling_time)  # Wait for signal to settle
        x_time_tmp, x_pos_tmp = bpm_object.get_x_sa_data(samples)  # record X pos
        y_time_tmp, y_pos_tmp = bpm_object.get_y_sa_data(samples)  # record Y pos
        x_time.append(x_time_tmp)
        x_pos.append(x_pos_tmp)
        y_time.append(y_time_tmp)
        y_pos.append(y_pos_tmp)
        output_power = np.append(output_power, rf_object.get_output_power()[0])
        input_power = np.append(input_power, bpm_object.get_input_power())

    # turn off the RF
    rf_object.turn_off_RF()

    specs = bpm_object.get_performance_spec()

    # Get the plot values in a format that is easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    upper_lim_x = int(floor(len(x_f_freq_baseline) / 2.))
    upper_lim_y = int(floor(len(y_f_freq_baseline) / 2.))
    format_plot.append(((x_time_baseline, x_pos_baseline),
                       ('Time (s)', 'Horizontal Beam Position (mm)', "Baseline_noise_x.pdf")))
    format_plot.append(((y_time_baseline, y_pos_baseline),
                       ('Time (s)', 'Vertical Beam Position (mm)', "Baseline_noise_y.pdf")))
    format_plot.append(((x_f_freq_baseline[0:upper_lim_x], x_f_data_baseline.real[0:upper_lim_x]),
                       ('Frequency (Hz)', 'Horizontal Beam Position', "Baseline_noise_spectrum_x.pdf")))
    format_plot.append(((y_f_freq_baseline[0:upper_lim_y], y_f_data_baseline.real[0:upper_lim_y]),
                       ('Frequency (Hz)', 'Vertical Beam Position', "Baseline_noise_spectrum_y.pdf")))
    format_plot.append(((y_time, y_pos),
                       ('Time (s)', 'Vertical Beam Position (mm)', "signal_to_noise_y.pdf")))

    if report_object is not None:
        intro_text = r"""Compares the noise generated.

            The RF signal is turned off, and then different parameters are measured from the BPM.  \\~\\
            """
        # Get the device names for the report
        device_names = []
        device_names.append(rf_object.get_device_id())
        device_names.append(bpm_object.get_device_id())
        # Get the parameter values for the report
        parameter_names = []
        parameter_names.append("Samples: " + str(samples))
        # add the test details to the report
        report_object.setup_test(test_name, intro_text, device_names, parameter_names)
        # make a caption and headings for a table of results
        caption = "Noise Results"
        headings = [["X Position", "Y Position", ], ["(mm)", "(mm)"]]
        data = [x_pos_baseline, y_pos_baseline]
        # copy the values to the report
        report_object.add_table_to_test('|c|c|', data, headings, caption)

    # plot all of the graphs
    for index in format_plot:
        if type(index[0][0]) is list:
            for ks in range(len(index[0][0])):
                plt.plot(index[0][0][ks], index[0][1][ks])
        else:
            plt.plot(index[0][0], index[0][1])

        plt.xlabel(index[1][0])
        plt.ylabel(index[1][1])
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
