from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
import numpy as np
import matplotlib.pyplot as plt
import time
from math import floor


def adc_test(rf_object,
             bpm_object,
             prog_atten_object,
             frequency,
             samples=10,
             power_levels=(-45., -60.),
             settling_time=1,
             report_object=None,
             sub_directory=""):
    """Compares the noise generated.

    The RF signal is turned off, and then different parameters are measured from the BPM. 

    Args:
        rf_object (RFSignalGenerator Obj): Object to interface with the RF hardware.
        bpm_object (BPMDevice Obj): Object to interface with the BPM hardware.
        prog_atten_object (Prog_Atten Obj): Object to interface with programmable attenuator hardware
        frequency (float): Output frequency for the tests, set as a float that will use the assumed units of MHz. 
        power_levels (tuple of floats): output power levels for the tests. dBm is assumed. 
        samples (int): Number of samples take.
        settling_time (float): Time in seconds, that the program will wait in between 
            setting an  output power on the RF, and reading the values of the BPM. 
        report_object (LaTeX Report Obj): Specific report that the test results will be recorded 
            to. If no report is sent to the test then it will just display the results in a graph. 
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
        float array: X ADC data read from the BPM
        float array: Y ADC data read from the BPM
    """

    # Formats the test name and tells the user the test has started
    test_name = __name__
    test_name = test_name.rsplit("Tests.")[1]
    test_name = test_name.replace("_", " ")
    print("Starting test \"" + test_name + "\"")

    # Initial setup of the RF system
    rf_object.turn_off_RF()
    rf_object.set_frequency(frequency)
    rf_object.set_output_power(power_levels[0])
    rf_object.turn_on_RF()
    time.sleep(settling_time)
    adc_n_bits = 16

    input_power = []
    output_power = []
    data1 = []
    data2 = []
    data3 = []
    data4 = []
    times = []
    for index in power_levels:
        # Set attenuator value to give desired power level.
        prog_atten_object.set_global_attenuation(power_levels[0] - index)
        time.sleep(settling_time)  # Wait for signal to settle
        time_tmp, data1_tmp, data2_tmp, data3_tmp, data4_tmp = bpm_object.get_ADC_data()  # record data
        rf_object.turn_off_RF()
        times.append(time_tmp)
        data1.append(data1_tmp)
        data2.append(data2_tmp)
        data3.append(data3_tmp)
        data4.append(data4_tmp)
        output_power = np.append(output_power, rf_object.get_output_power()[0])
        input_power = np.append(input_power, bpm_object.get_input_power())

    # turn off the RF
    rf_object.turn_off_RF()


    # Get the plot values in a format that is easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    format_plot.append(((times, data1), ('bit number', 'counts', "ADC1_histogram.pdf")))
    format_plot.append(((times, data2), ('bit number', 'counts', "ADC2_histogram.pdf")))
    format_plot.append(((times, data3), ('bit number', 'counts', "ADC3_histogram.pdf")))
    format_plot.append(((times, data4), ('bit number', 'counts', "ADC4_histogram.pdf")))

    if report_object is not None:
        intro_text = r"""Excites with a sine wave and then gets the ADC data from each channel. 
        Plots the histogram to that any missing bits can be identified.

        The RF signal is a sine wave.  \\~\\
        """
        # Get the device names for the report
        device_names = []
        device_names.append(rf_object.get_device_ID())
        device_names.append(bpm_object.get_device_ID())

        # Get the parameter values for the report
        parameter_names = []
        parameter_names.append("Samples: " + str(samples))
        # add the test details to the report
        report_object.setup_test(test_name, intro_text, device_names, parameter_names)

    # plot all of the graphs
    adc_max_counts = np.power(2, adc_n_bits)
    adc_step = adc_max_counts / adc_n_bits
    bin_edges = range(adc_n_bits + 1)
    for index in format_plot:
        plt.hist(np.transpose(np.floor(index[0][1] / adc_step)), bins=bin_edges)
        plt.xlabel(index[1][0])
        plt.ylabel(index[1][1])
        if report_object is None:
            # If no report is entered as an input to the test, simply display the results
            plt.show()
        else:
            plt.savefig(''.join((sub_directory, index[1][2])))
            report_object.add_figure_to_test(image_name=''.join((sub_directory, index[1][2])), caption=index[1][2])
        plt.cla()  # Clear axis
        plt.clf()  # Clear figure

    # return the full data sets
    return
