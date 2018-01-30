from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
import numpy as np
import matplotlib.pyplot as plt
import time


def beam_power_dependence(
                          rf_object,
                          bpm_object,
                          prog_atten_object,
                          frequency,
                          power_levels=range(-40, -100, -10),
                          settling_time=1,
                          report_object=None,
                          sub_directory=""):
    """Tests the relationship between RF output power and values read from the BPM.

    An RF signal is output, and then different parameters are measured from the BPM. 
    The signal is linearly ramped up in dBm at a single frequency. The number of samples to take, 
    and settling time between each measurement can be decided using the arguments. 

    Args:
        rf_object (RFSignalGenerator Obj): Object to interface with the RF hardware.
        bpm_object (BPMDevice Obj): Object to interface with the BPM hardware.
        prog_atten_object (Prog_Atten Obj): Object to interface with programmable attenuator hardware
        frequency (float): Output frequency for the tests, set as a float that will
            use the assumed units of MHz. 
        power_levels (list): The desired power levels to run the test at.
                             default value is [-40, -50, -60, -70, -80, -90].
                             The values are floats and dBm is assumed.
        settling_time (float): Time in seconds, that the program will wait in between 
            setting an  output power on the RF, and reading the values of the BPM. 
        report_object (LaTeX Report Obj): Specific report that the test results will be recorded
            to. If no report is sent to the test then it will just display the results in 
            a graph. 
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
        float array: Power output from the RF
        float array: Power read at the BPM
        float array: Beam Current read at the BPM
        float array: X Positions read from the BPM
        float array: Y Positions read from the BPM
    """

    # Informs the user the test has started
    test_name = __name__
    test_name = test_name.rsplit("Tests.")[1]
    test_name = test_name.replace("_", " ")
    print("Starting test \"" + test_name + "\"")

    # Set the initial state of the RF device and programmable attenuator.
    rf_object.turn_off_RF()
    rf_object.set_frequency(frequency)
    rf_object.set_output_power(power_levels[0])
    prog_atten_object.set_global_attenuation(0)
    rf_object.turn_on_RF()
    time.sleep(settling_time)

    # Build up the arrays where the final values will be saved
    x_pos = np.array([])
    y_pos = np.array([])
    beam_current = np.array([])
    output_power = np.array([])
    input_power = np.array([])
    adc_sum = np.array([])

    # Perform the test
    for index in power_levels:
        # Set attenuator value to give desired power level.
        prog_atten_object.set_global_attenuation(power_levels[0] - index)
        time.sleep(settling_time)  # Wait for signal to settle
        beam_current = np.append(beam_current, bpm_object.get_beam_current())  # record beam current
        x_pos = np.append(x_pos, bpm_object.get_x_position())  # record X pos
        y_pos = np.append(y_pos, bpm_object.get_y_position())  # record Y pos
        input_power = np.append(input_power, bpm_object.get_input_power())
        adc_sum = np.append(adc_sum, bpm_object.get_adc_sum())

    # turn off the RF
    rf_object.turn_off_RF()

    specs = bpm_object.get_performance_spec()

    # Get the plot values in a format that's easy to iterate
    format_plot = [] # x axis, y axis, x axis title, y axis title, title of file, caption
    format_plot.append(((power_levels, input_power),
                       ('RF Source Power Output (dBm)', 'Power input at BPM (dBm)', "power_vs_power.pdf")))
    format_plot.append(((power_levels, beam_current),
                       ('RF Source Power Output (dBm)', 'Beam Current at BPM (mA)', "power_vs_current.pdf")))
    format_plot.append(((power_levels, x_pos),
                       ('RF Source Power Output (dBm)', 'Horizontal Beam Position (mm)', "power_vs_X.pdf"),
                       specs['Beam_power_dependence_X']))
    format_plot.append(((power_levels, y_pos),
                       ('RF Source Power Output (dBm)', 'Vertical Beam Position (mm)', "power_vs_Y.pdf"),
                       specs['Beam_power_dependence_Y']))
    format_plot.append(((power_levels, adc_sum),
                       ('RF Source Power Output (dBm)', 'ADC Sum (counts)', 'power_vs_ADC_sum.pdf')))

    if report_object is not None:
        intro_text = r"""Tests the relationship between RF output power and values read from the BPM. 
        An RF signal is output, and then different parameters are measured from the BPM. 
        The signal is linearly ramped up in dBm at a single frequency. The number of samples to take, 
        and settling time between each measurement can be decided using the arguments. \\~\\
        """
        # Get the device names for the report
        device_names = []
        device_names.append(rf_object.get_device_id())
        device_names.append(bpm_object.get_device_id())
        # Get the parameter values for the report
        parameter_names = []
        parameter_names.append("Frequency: " + str(frequency) + "MHz")
        parameter_names.append("Power levels used: " + str(power_levels) + "dBm")
        parameter_names.append("Settling time: " + str(settling_time) + "s")
        # add the test details to the report
        report_object.setup_test(test_name, intro_text, device_names, parameter_names)
        # make a caption and headings for a table of results
        caption = "Beam Power Dependence Results"
        headings = [["Output Power", "Input Power", "BPM Current", "X Position", "Y Position", "ADC Sum"],
                    ["(dBm)", "(dBm)", "(mA)", "(mm)", "(mm)", "(Counts)"]]
        data = [output_power, input_power, beam_current, x_pos, y_pos, adc_sum]
        # copy the values to the report
        report_object.add_table_to_test('|c|c|c|c|c|c|', data, headings, caption)

    # plot all of the graphs
    for index in format_plot:
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
    return output_power, input_power, beam_current, x_pos, y_pos
