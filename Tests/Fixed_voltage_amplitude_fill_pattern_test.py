from framework_requires import BaseTestClass
import RFSignalGenerators
import BPMDevice
import Gate_Source
from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
require("scipy")
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.io import savemat


def fixed_voltage_amplitude_fill_pattern_test(
                                   test_system_object,
                                   rf_object,
                                   bpm_object,
                                   prog_atten_object,
                                   gate_source_object,
                                   frequency,
                                   max_power=-40,
                                   duty_cycles=np.arange(1, 0, -0.1),
                                   pulse_period=1.87319,
                                   settling_time=1,
                                   samples=10,
                                   report_object=None,
                                   sub_directory=""):
    """
        This test imitates a fill pattern by modulation the RF signal with a square wave. The up time 
        of the square wave represents when a bunch goes passed, and the downtime the gaps between the 
        bunches. This test will take the pulse length in micro seconds, and then linearly step up the 
        duty cycle of the pulse, from 0.1 to 1. Readings on the BPM are then recorded as the duty cycle
        is changed. While the duty cycle is increased, the peak RF voltage stays fixed, meaning that 
        the average power will change with duty cycle. 
        

        Args:
            test_system_object (System Obj): Object capturing the system losses and hardware ids.
            rf_object (RFSignalGenerator Obj): Object to interface with the RF hardware.
            bpm_object (BPMDevice Obj): Object to interface with the BPM hardware.
            prog_atten_object (Prog_Atten Obj): Object to interface with programmable attenuator hardware
            gate_source_object: (GateSource Obj): Object used to interface with the gate source
                hardware. 
            frequency (float/str): Output frequency for the tests, set as a float that will 
                use the assumed units of MHz. 
            max_power (float): Starting output power for the tests, default value is
                -100 dBm. The input values are floats and dBm is assumed. 
            duty_cycles (list): The duty cycles to be used in the test. Values need to be in descending order.
            pulse_period (float): The pulse period for the modulation signal, i.e. the bunch length, 
                this is a float that is in micro seconds.
            settling_time (float): Time in seconds, that the program will wait in between 
                setting an  output power on the RF, and reading the values of the BPM. 
            samples (int): The number of samples to capture at each data point.
            report_object (LaTeX Report Obj): Specific report that the test results will be recorded
                to. If no report is sent to the test then it will just display the results in 
                a graph. 
            sub_directory (str): String that can change where the graphs will be saved to
                
        Returns:
            float array: duty cycle of the modulation signal
            float array: power read from the BPM
            float array: current read from the BPM
            float array: X position read from the BPM
            float array: Y position read from the BPM


    """
    test_name = test_system_object.test_initialisation(test_name=__name__,
                                                       rf_object=rf_object,
                                                       prog_atten_object=prog_atten_object,
                                                       bpm_object=bpm_object,
                                                       frequency=frequency,
                                                       power_level=max_power)

    gate_source_object.set_pulse_period(pulse_period)
    gate_source_object.turn_on_modulation()
    gate_source_object.set_pulse_dutycycle(duty_cycles[0])
    # Set up BPM for normal operation
    bpm_object.set_internal_state()
    # Wait for system to settle
    time.sleep(5)

    # Build up the arrays where the final values will be saved
    x_pos_mean = np.array([])
    y_pos_mean = np.array([])
    x_pos_std = np.array([])
    y_pos_std = np.array([])

    for index in duty_cycles:
        gate_source_object.set_pulse_dutycycle(index)
        time.sleep(settling_time)
        #bpm_power = np.append(bpm_power, bpm_object.get_input_power())
        x_time, x_pos_data = bpm_object.get_x_sa_data(samples)  # record X pos
        y_time, y_pos_data = bpm_object.get_y_sa_data(samples)  # record Y pos

        x_pos_mean = np.append(x_pos_mean, np.mean(x_pos_data))  # record X pos
        y_pos_mean = np.append(y_pos_mean, np.mean(y_pos_data))  # record Y pos
        x_pos_std = np.append(x_pos_std, np.std(x_pos_data))  # record X pos
        y_pos_std = np.append(y_pos_std, np.std(y_pos_data))  # record Y pos

    rf_object.turn_off_RF()
    gate_source_object.turn_off_modulation()

    savemat(sub_directory + "constant_fill_charge_fill_sweep_data" + ".mat",
            {'duty_cycles': duty_cycles,
             'x_pos_mean': x_pos_mean,
             'x_pos_std': x_pos_std,
             'y_pos_mean': y_pos_mean,
             'y_pos_std': y_pos_std})

    # Get the plot values in a format thats easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    format_plot.append(((duty_cycles, x_pos_mean, x_pos_std),
                        ('Gating signal duty cycle (0-1)', 'Horizontal Beam Position (mm)',
                        "Duty_cycle_vs_X.pdf")))
    format_plot.append(((duty_cycles, x_pos_mean, x_pos_std),
                        ('Gating signal duty cycle (0-1)', 'Vertical Beam Position (mm)',
                        "Duty_cycle_vs_Y.pdf")))

    if report_object is not None:
        intro_text = r"""
            Equivalent to keeping the total charge in the train constant.
            This test imitates a fill pattern by modulation the RF signal with a square wave. The up time 
            of the square wave represents when a bunch goes passed, and the downtime the gaps between the 
            bunches. This test will take the pulse length in micro seconds, and then linearly step up the 
            duty cycle of the pulse, from 0.1 to 1. Readings on the BPM are then recorded as the duty cycle
            is changed. While the duty cycle is increased, the peak RF voltage stays fixed, meaning that 
            the average power will change with duty cycle. \\~\\
        """

        device_names = []
        device_names.append('RF source is ' + rf_object.get_device_id())
        device_names.append('Gate is ' + gate_source_object.get_device_id())
        device_names.append('BPM is ' + bpm_object.get_device_id())
        # Get the parameter values for the report
        parameter_names = []
        parameter_names.append("Frequency: " + rf_object.get_frequency()[1])
        parameter_names.append("Output Power: " + str(max_power) + "dBm")
        parameter_names.append("Pulse Period: " + gate_source_object.get_pulse_period()[1])
        parameter_names.append("Settling time: " + str(settling_time) + "s")
        # add the test details to the report
        report_object.setup_test(test_name, intro_text, device_names, parameter_names)

        # make a caption and headings for a table of results
        caption = "Changing gate duty cycle, with fixed RF amplitude "
        headings = [["Duty Cycle", "mean X Position", "mean Y Position", "Std X", "Std Y"],
                    ["(0-1)", "(mm)", "(mm)", "", ""]]
        data = [duty_cycles, x_pos_mean, y_pos_mean, x_pos_std, y_pos_std]

        # copy the values to the report
        report_object.add_table_to_test('|c|c|c|c|c|', data, headings, caption)

    # plot all of the graphs
    for index in format_plot:
        plt.errorbar(index[0][0], index[0][1], index[0][2])
        plt.xlabel(index[1][0])
        plt.ylabel(index[1][1])
        plt.grid(True)
        if report_object is None:
            # If no report is entered as an input to the test, simply display the results
            plt.show()
        else:
            plt.savefig(''.join((sub_directory, index[1][2])))
            report_object.add_figure_to_test(image_name=''.join((sub_directory, index[1][2])), caption=index[1][2])
        plt.cla()  # Clear axis
        plt.clf()  # Clear figure


