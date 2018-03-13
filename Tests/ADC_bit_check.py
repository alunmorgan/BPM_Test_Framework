from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
import numpy as np
import matplotlib.pyplot as plt
import time
from math import floor
from scipy.io import savemat


def adc_test(
             test_system_object,
             rf_object,
             bpm_object,
             prog_atten_object,
             frequency,
             power_level=-20,
             settling_time=1,
             report_object=None,
             sub_directory=""):
    """Compares the signals from the ADCs while a sine wave excitation is input.

    The RF signal is turned off, and then different parameters are measured from the BPM. 

    Args:
        test_system_object (System Obj): Object capturing the system losses and hardware ids.
        rf_object (RFSignalGenerator Obj): Object to interface with the RF hardware.
        bpm_object (BPMDevice Obj): Object to interface with the BPM hardware.
        prog_atten_object (Prog_Atten Obj): Object to interface with programmable attenuator hardware
        frequency (float): Output frequency for the tests, set as a float that will use the assumed units of MHz. 
        power_level (float): output power level for the tests. dBm is assumed.
        settling_time (float): Time in seconds, that the program will wait in between
            setting an  output power on the RF, and reading the values of the BPM. 
        report_object (LaTeX Report Obj): Specific report that the test results will be recorded 
            to. If no report is sent to the test then it will just display the results in a graph. 
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
    """
    test_name = test_system_object.test_initialisation(__name__, rf_object, prog_atten_object, frequency, power_level)
    bpm_object.set_internal_state(agc='AGC off', delta=0, offset=0, switches='Manual',
                                  switch_state=15, attenuation=0, dsc='Unity gains',
                                  ft_state='Enabled')
    # Wait for signal to settle
    time.sleep(settling_time)

    if report_object is not None:
        intro_text = r"""Excites with a sine wave and then gets the ADC data from each channel. 
        Plots the histogram to that any missing bits can be identified. The expected value is 0.5. 
        Any value 0.1 away from this indicates a problem.

        The RF signal is a sine wave.  \\~\\
        """
        # Get the device names for the report
        device_names = []
        device_names.append('RF source is ' + test_system_object.rf_hw)
        device_names.append('BPM is ' + test_system_object.bpm_hw)

        # Get the parameter values for the report
        parameter_names = []
        # add the test details to the report
        report_object.setup_test(test_name, intro_text, device_names, parameter_names)

    # Setting up variables.
    data = np.empty((1024, bpm_object.adc_n_bits, bpm_object.num_adcs))
    data_std = np.empty((bpm_object.adc_n_bits, bpm_object.num_adcs))

    # Gets 1024 samples for each ADC.
    time_tmp, data1_tmp, data2_tmp, data3_tmp, data4_tmp = bpm_object.get_adc_data()  # record data

    # turn off the RF
    rf_object.turn_off_RF()

    #  Converting to arrays of binary values
    # First convert the int value into a binary string.
    # Turn that sting into a list of values.
    # Then turn that list of lists into an array
    data[:, :, 0] = np.asarray([list(format(x, '0' + str(bpm_object.adc_n_bits) + 'b')) for x in data1_tmp])
    data[:, :, 1] = np.asarray([list(format(x, '0' + str(bpm_object.adc_n_bits) + 'b')) for x in data2_tmp])
    data[:, :, 2] = np.asarray([list(format(x, '0' + str(bpm_object.adc_n_bits) + 'b')) for x in data3_tmp])
    data[:, :, 3] = np.asarray([list(format(x, '0' + str(bpm_object.adc_n_bits) + 'b')) for x in data4_tmp])

    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption

    for kw in range(bpm_object.num_adcs):
        for wn in range(bpm_object.adc_n_bits):
            data_std[wn, kw] = np.std(data[:, wn, kw])
        format_plot.append(((np.arange(1, bpm_object.adc_n_bits + 1), data_std[:, kw]),
                            ('bit number', 'Standard deviation', ' '.join(('ADC', str(kw + 1))),
                             'ADC_bit_check.pdf')))

    savemat(''.join((sub_directory, 'ADC_bit_check', '_data.mat')),
            {'data': data,
             'data_std': data_std})

    # plot all of the graphs
    cols = ['k', 'r', 'g', 'b']
    x_shift = 0
    cols_ind = 0
    for index in format_plot:
        plt.bar(index[0][0] + x_shift, index[0][1], align='center', width=0.15, label=index[1][2], color=cols[cols_ind])
        x_shift = x_shift + 0.1
        cols_ind = cols_ind + 1
    plt.legend(loc='upper right')
    plt.xlabel(format_plot[0][1][0])
    plt.ylabel(format_plot[0][1][1])
    plt.xlim(0.5, bpm_object.adc_n_bits + 1)
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


