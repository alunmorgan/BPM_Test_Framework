import RFSignalGenerators
import BPMDevice
import Gate_Source
from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
import numpy as np
import matplotlib.pyplot as plt
import time


def scaled_voltage_amplitude_fill_pattern_test(
                                   rf_object,
                                   bpm_object,
                                   prog_atten_object,
                                   gate_source_object,
                                   frequency,
                                   max_power=-40,
                                   duty_cycles=np.arange(1, 0, -0.1),
                                   pulse_period=1.87319,
                                   settling_time=1,
                                   report_object=None,
                                   sub_directory=""):
    """
        This test imitates a fill pattern by modulation the RF signal with a square wave. The up time 
        of the square wave represents when a bunch goes passed, and the downtime the gaps between the 
        bunches. This test will take the pulse length in micro seconds, and then linearly step up the 
        duty cycle of the pulse, from 0.1 to 1. Readings on the BPM are then recorded as the duty cycle
        is changed. While the duty cycle is increased, the peak RF voltage increases, meaning that 
        the average power will be constant with duty cycle change. 


        Args:
            rf_object (RFSignalGenerator Obj): Object to interface with the RF hardware.
            bpm_object (BPMDevice Obj): Object to interface with the BPM hardware.
            prog_atten_object (Prog_Atten Obj): Object to interface with programmable attenuator hardware
            gate_source_object: (GateSource Obj): Object used to interface with the gate source
                hardware. 
            frequency (float/str): Output frequency for the tests, set as a float that will 
                use the assumed units of MHz. 
            max_power (float): Starting output power for the tests, default value is -40 dBm.
            duty_cycles (list): The duty cycles to be used in the test. Values need to be in descending order.
            pulse_period (float): The pulse period for the modulation signal, i.e. the bunch length,
                this is a float that is in micro seconds.
            settling_time (float): Time in seconds, that the program will wait in between 
                setting an  output power on the RF, and reading the values of the BPM. 
            report_object (LaTeX Report Obj): Specific report that the test results will be recorded
                to. If no report is sent to the test then it will just display the results in 
                a graph. 
            sub_directory (str): String that can change where the graphs will be saved to
        Returns:
            float array: duty cycle of the modulation signal
            float array: power set at the rf output
            float array: power read from the BPM
            float array: current read from the BPM
            float array: X position read from the BPM
            float array: Y position read from the BPM
    """

    test_name = __name__
    test_name = test_name.rsplit("Tests.")[1]
    test_name = test_name.replace("_", " ")
    print("Starting test \"" + test_name + "\"")

    rf_object.set_frequency(frequency)
    rf_object.set_output_power(max_power)
    prog_atten_object.set_global_attenuation(0)
    gate_source_object.set_pulse_period(pulse_period)
    gate_source_object.turn_on_modulation()
    gate_source_object.set_pulse_dutycycle(duty_cycles[0])
    rf_object.turn_on_RF()
    time.sleep(settling_time)

    bpm_power = np.array([])
    bpm_xpos = np.array([])
    bpm_ypos = np.array([])
    bpm_current = np.array([])
    rf_output = np.array([])
    adc_sum = np.array([])

    for index in duty_cycles:
        gate_source_object.set_pulse_dutycycle(index)
        power_adjustment = np.absolute(20*np.log10(index))
        prog_atten_object.set_global_attenuation(power_adjustment)
        time.sleep(settling_time)
        rf_output = np.append(rf_output, max_power - power_adjustment)
        bpm_power = np.append(bpm_power, bpm_object.get_input_power())
        bpm_current = np.append(bpm_current, bpm_object.get_beam_current())
        bpm_xpos = np.append(bpm_xpos, bpm_object.get_X_position())
        bpm_ypos = np.append(bpm_ypos, bpm_object.get_Y_position())
        adc_sum = np.append(adc_sum, bpm_object.get_ADC_sum())

    rf_object.turn_off_RF()
    gate_source_object.turn_off_modulation()

    # Get the plot values in a format thats easy to iterate
    format_plot = []  # x axis, y axis, x axis title, y axis title, title of file, caption
    format_plot.append((duty_cycles, rf_output, 'Gating signal duty cycle (0-1)', 'RF power ar source (dBm)',
                        "scaled_DC_vs_Out_power.pdf"))
    format_plot.append((duty_cycles, bpm_power, 'Gating signal duty cycle (0-1)', 'Power input at BPM (dBm)',
                        "scaled_DC_vs_In_power.pdf"))
    format_plot.append((duty_cycles, bpm_current, 'Gating signal duty cycle (0-1)', 'Beam Current at BPM (mA)',
                        "scaled_DC_vs_current.pdf"))
    format_plot.append((duty_cycles, bpm_xpos, 'Gating signal duty cycle (0-1)', 'Horizontal Beam Position (mm)',
                        "scaled_DC_vs_X.pdf"))
    format_plot.append((duty_cycles, bpm_ypos, 'Gating signal duty cycle (0-1)', 'Vertical Beam Position (mm)',
                        "scaled_DC_vs_Y.pdf"))
    format_plot.append((duty_cycles, adc_sum, 'Gating signal duty cycle (0-1)', 'ADC Sum (counts)',
                        "scaled_DC_vs_ADC_Sum.pdf"))

    if report_object is not None:
        intro_text = r"""
            This test imitates a fill pattern by modulation the RF signal with a square wave. The up time 
            of the square wave represents when a bunch goes passed, and the downtime the gaps between the 
            bunches. This test will take the pulse length in micro seconds, and then linearly step up the 
            duty cycle of the pulse, from 0.1 to 1. Readings on the BPM are then recorded as the duty cycle
            is changed. While the duty cycle is increased, the peak RF voltage increases, meaning that 
            the average power will be constant with duty cycle change. \\~\\
        """
        device_names = []
        device_names.append(rf_object.get_device_ID())
        device_names.append(gate_source_object.get_device_ID())
        device_names.append(bpm_object.get_device_ID())

        # Get the parameter values for the report
        parameter_names = []
        parameter_names.append("Frequency: " + rf_object.get_frequency()[1])
        parameter_names.append("Maximum Power: " + str(max_power) + "dBm")
        parameter_names.append("Pulse Period: " + gate_source_object.get_pulse_period()[1])
        parameter_names.append("Settling time: " + str(settling_time) + "s")
        # add the test details to the report
        report_object.setup_test(test_name, intro_text, device_names, parameter_names)
        # make a caption and headings for a table of results
        caption = "Changing gate duty cycle, with fixed RF amplitude "
        headings = [["Duty Cycle", "Output Power", "Input Power", "BPM Current", "X Position", "Y Position", "ADC Sum"],
                    ["(0-1)", "(dBm)", "(dBm)", "(mA)", "(mm)", "(mm)", "(Counts)"]]
        data = [duty_cycles, rf_output, bpm_power, bpm_current, bpm_xpos, bpm_ypos, adc_sum]
        # copy the values to the report
        report_object.add_table_to_test('|c|c|c|c|c|c|c|', data, headings, caption)

    # plot all of the graphs
    for index in format_plot:
        plt.plot(index[0], index[1])
        plt.xlabel(index[2])
        plt.ylabel(index[3])
        plt.grid(True)
        if report_object is None:
            # If no report is entered as an input to the test, simply display the results
            plt.show()
        else:
            plt.savefig(''.join((sub_directory, index[4])))
            report_object.add_figure_to_test(image_name=''.join((sub_directory, index[4])), caption=index[4])

        plt.cla()  # Clear axis
        plt.clf()  # Clear figure

    # return the full data sets
    return duty_cycles, rf_output, bpm_power, bpm_current, bpm_xpos, bpm_ypos
