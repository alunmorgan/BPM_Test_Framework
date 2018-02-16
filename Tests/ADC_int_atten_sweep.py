from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
import numpy as np
import matplotlib.pyplot as plt
import time
from math import floor


def adc_int_atten_sweep_test(rf_object,
                             bpm_object,
                             prog_atten_object,
                             frequency,
                             power_level=-20,
                             attenuation_levels=np.arange(6, 35, 3),
                             settling_time=1,
                             report_object=None,
                             sub_directory=""):
    """Compares the signals from the ADCs while a sine wave excitation is input.

    The RF signal is turned off, and then different parameters are measured from the BPM.

    Args:
        rf_object (RFSignalGenerator Obj): Object to interface with the RF hardware.
        bpm_object (BPMDevice Obj): Object to interface with the BPM hardware.
        prog_atten_object (Prog_Atten Obj): Object to interface with programmable attenuator hardware
        frequency (float): Output frequency for the tests, set as a float that will use the assumed units of MHz.
        power_levels (tuple of floats): output power levels for the tests. dBm is assumed.
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

    # Initial setup of the RF system.
    rf_object.turn_off_RF()
    rf_object.set_frequency(frequency)
    # Forcing to be an int as decimal points will cause the command sent to fail
    rf_object.set_output_power(int(power_level))
    prog_atten_object.set_global_attenuation(0)
    rf_object.turn_on_RF()
    bpm_object.set_attenuation(6)
    time.sleep(settling_time)
    adc_n_bits = 16

    adc_max_counts = np.power(2, adc_n_bits)
    adc_step = adc_max_counts / adc_n_bits
    bin_edges = range(adc_n_bits + 1)

    input_power = []
    output_power = []
    data1 = []
    data2 = []
    data3 = []
    data4 = []
    times = []
    graph_legend = []
    #  Gradually reducing the power level
    for index in attenuation_levels:
        # Set attenuator value to give desired power level.
        bpm_object.set_attenuation(index)
        time.sleep(settling_time)  # Wait for signal to settle
        # Gets 1024 samples for each ADC.
        time_tmp, data1_tmp, data2_tmp, data3_tmp, data4_tmp = bpm_object.get_adc_data()  # record data
        times.append(time_tmp)
        #  Identifying which bit bin a value is in.
        data1_tmp[:] = [x / adc_step for x in data1_tmp]
        data2_tmp[:] = [x / adc_step for x in data2_tmp]
        data3_tmp[:] = [x / adc_step for x in data3_tmp]
        data4_tmp[:] = [x / adc_step for x in data4_tmp]
        data1.append(data1_tmp)
        data2.append(data2_tmp)
        data3.append(data3_tmp)
        data4.append(data4_tmp)
        output_power.append(index)
        input_power.append(bpm_object.get_input_power())
        graph_legend.append(str(index))

    # turn off the RF
    rf_object.turn_off_RF()
    # Get the plot values in a format that is easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    format_plot.append(((times, data1), ('bit number', 'counts',
                                         "ADC1_histogram_varying_internal_attenuation.pdf", graph_legend)))
    format_plot.append(((times, data2), ('bit number', 'counts',
                                         "ADC2_histogram_varying_internal_attenuation.pdf", graph_legend)))
    format_plot.append(((times, data3), ('bit number', 'counts',
                                         "ADC3_histogram_varying_internal_attenuation.pdf", graph_legend)))
    format_plot.append(((times, data4), ('bit number', 'counts',
                                         "ADC4_histogram_varying_internal_attenuation.pdf", graph_legend)))

    if report_object is not None:
        intro_text = r"""Excites with a sine wave and then gets the ADC data from each channel. 
        Plots the histogram to that any missing bits can be identified.

        The RF signal is a sine wave.  \\~\\
        """
        # Get the device names for the report
        device_names = []
        device_names.append('RF source is ' + rf_object.get_device_id())
        device_names.append('BPM is ' + bpm_object.get_device_id())

        # Get the parameter values for the report
        parameter_names = []
        parameter_names.append('Attenuation levels: ' + str(attenuation_levels))
        # add the test details to the report
        report_object.setup_test(test_name, intro_text, device_names, parameter_names)

    # plot all of the graphs

    for index in format_plot:
        #if len(index[1]) == 4:
        plt.hist(np.transpose(np.array(index[0][1])), bins=bin_edges, label=index[1][3])
        #else:
        #    plt.hist(np.transpose(np.array(index[0][1])), bins=bin_edges)
        plt.legend()
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
