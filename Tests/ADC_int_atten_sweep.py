from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
import numpy as np
import matplotlib.pyplot as plt
import time
from math import floor
from scipy.io import savemat


def adc_int_atten_sweep_test(
                             test_system_object,
                             rf_object,
                             bpm_object,
                             prog_atten_object,
                             frequency,
                             power_level=-20,
                             external_attenuation=60,
                             attenuation_levels=np.arange(0, 62, 2),
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
        power_levels (tuple of floats): output power levels for the tests. dBm is assumed.
        external_attenuation (int): The level of external attenuation used in order to set the initial
                                    power level at the BPM.
        settling_time (float): Time in seconds, that the program will wait in between
            setting an  output power on the RF, and reading the values of the BPM.
        report_object (LaTeX Report Obj): Specific report that the test results will be recorded
            to. If no report is sent to the test then it will just display the results in a graph.
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
        float array: X ADC data read from the BPM
        float array: Y ADC data read from the BPM
    """
    test_name = test_system_object.test_initialisation(__name__, rf_object, prog_atten_object,
                                                       bpm_object, frequency, power_level,
                                                       external_attenuation=external_attenuation)
    bpm_object.set_internal_state(agc='AGC off', delta=0, offset=0, switches='Manual',
                                  switch_state=bpm_object.switch_straight, attenuation=0, dsc='Unity gains',
                                  ft_state='Enabled')
    # Wait for system to settle
    time.sleep(settling_time)

    if report_object is not None:
        intro_text = r"""Excites with different signal levels. Gets the ADC data from each channel at each signal level. 
        Plots the curve.

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

    num_repeat_points = 10
    data = np.empty((len(attenuation_levels), 1024, bpm_object.num_adcs, num_repeat_points))
    data_adj = np.zeros((len(attenuation_levels), bpm_object.num_adcs))

    #  Gradually reducing the power level
    level_ind = 0
    upper_atten = attenuation_levels[0]
    atten_step = 2  # The drop in attenuation allowed before the external attenuation is adjusted.
    for index in attenuation_levels:
        data_adj_before = np.empty((1024, bpm_object.num_adcs))
        data_adj_after = np.empty((1024, bpm_object.num_adcs))
        _1, data_adj_before[:, 0], \
            data_adj_before[:, 1], \
            data_adj_before[:, 2], \
            data_adj_before[:, 3] = bpm_object.get_adc_data(bpm_object.adc_n_bits)
        time.sleep(settling_time)  # Wait for signal to settle
        prog_atten_object.set_global_attenuation(external_attenuation - index)
        _1, data_adj_after[:, 0], \
            data_adj_after[:, 1], \
            data_adj_after[:, 2], \
            data_adj_after[:, 3] = bpm_object.get_adc_data(bpm_object.adc_n_bits)
        data_adj[level_ind, :] = np.max(data_adj_after, axis=0) - \
                                 np.max(data_adj_before, axis=0) #+ data_adj[level_ind - 1, :]
        bpm_object.set_attenuation(index)
        time.sleep(settling_time)  # Wait for signal to settle
        # Gets 1024 samples for each ADC.
        for nw in range(num_repeat_points):
            time_tmp, data[level_ind, :, 0, nw], \
                      data[level_ind, :, 1, nw], \
                      data[level_ind, :, 2, nw], \
                      data[level_ind, :, 3, nw] = bpm_object.get_adc_data(bpm_object.adc_n_bits)  # record data
        level_ind = level_ind + 1

    # turn off the RF
    rf_object.turn_off_RF()

    data_max = np.mean(np.max(data, axis=1), axis=2)
    data_std = np.std(np.max(data, axis=1), axis=2)
    data_corrected = data_max - data_adj
    savemat(sub_directory + "ADC_int_atten_sweep_data" + ".mat",
            {'attenuation': attenuation_levels,
             'data': data,
             'data_max': data_max,
             'data_std': data_std,
             'data_adj': data_adj,
             'data_corrected': data_corrected})

    # Get the plot values in a format that is easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    for hw in range(bpm_object.num_adcs):
        format_plot.append(((attenuation_levels, data_corrected[:, hw], data_std[:, hw]), ('attenuation', 'counts',
                            "ADC_varying_internal_attenuation.pdf", ' '.join(('ADC', str(hw))))))

    # plot all of the graphs
    cols = ['k', 'r', 'g', 'b']
    cols_ind = 0
    for index in format_plot:
        plt.plot(index[0][0], index[0][1], color=cols[cols_ind], label=index[1][3])
        cols_ind = cols_ind + 1
    plt.legend(loc='upper right')
    plt.xlabel(format_plot[0][1][0])
    plt.ylabel(format_plot[0][1][1])
    plt.xlim(attenuation_levels[0], attenuation_levels[-1])
    if report_object is None:
        # If no report is entered as an input to the test, simply display the results
        plt.show()
    else:
        plt.savefig(''.join((sub_directory, format_plot[0][1][2])))
        report_object.add_figure_to_test(image_name=''.join((sub_directory, format_plot[0][1][2])),
                                         caption='Internal attenuator check')
    plt.cla()  # Clear axis
    plt.clf()  # Clear figure

