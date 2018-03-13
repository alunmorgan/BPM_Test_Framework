from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
require("scipy")
import numpy as np
import matplotlib.pyplot as plt
import time
import itertools
from scipy.io import savemat


def calc_x_pos(a, b, c, d):
    diff = ((a+d)-(b+c))
    total = (a+b+c+d)
    kx = 10.0
    x = kx*(diff/total)
    return x


def calc_y_pos(a, b, c, d):
    diff = ((a+b)-(c+d))
    total = (a+b+c+d)
    ky = 10.0
    y = ky*(diff/total)
    return y


def quarter_round(x):
    return round(x * 4) / 4


def beam_position_equidistant_grid_raster_scan_test(
             test_system_object,
             rf_object,
             bpm_object,
             prog_atten_object,
             rf_power,
             rf_frequency,
             nominal_attenuation,
             x_points,
             y_points,
             settling_time,
             report_object=None,
             sub_directory=""):
    """Moves the beam position to -5 to 5 in the XY plane and recods beam position

    The calc_x_pos and calc_y_pos functions are used to measure the theoretical beam position values.
    A set of ABCD values are created that will move the beam position from -5 to 5 in both the X and Y
    plane. This is then converted into attenuation values to put into the attenuator. A fixed RF frequency 
    and power is used while the attenuator values are changed. Finally the predicted values are compared 
    with the measured values of position. 

        Args:
            rf_object (RFSignalGenerator Obj): Object to interface with the RF hardware.
            bpm_object (BPMDevice Obj): Object to interface with the BPM hardware.
            prog_atten_object (Prog_Atten Obj): Object to interface with programmable attenuator hardware
            rf_power (float): Output power of the RF system throughout the test, in dBm 
            rf_frequency (float): Frequency output of the RF throughout the test, in MHz
            nominal_attenuation (float): starting attenuation values of each attenuator, in dB
            x_points (int): number of samples in the X plane
            y_points (int) number of samples in the Y plane 
            settling_time (float): time in seconds to wait between changing an attenuator value and 
                taking a reading from the BPM. 
            report_object (LaTeX Report Obj): Specific report that the test results will be recorded
                to. If no report is sent to the test then it will just display the results in 
                a graph. 
            sub_directory (str): String that can change where the graphs will be saved to
                
        Returns:
            float array: measured X values of position
            float array: measured Y values of position
            float array: predicted X values of position
            float array: predicted Y values of position
    """
    # Initialise test
    test_name = test_system_object.test_initialisation(__name__, rf_object, prog_atten_object,
                                                       rf_frequency, power_level)
    # Set up BPM for normal operation
    bpm_object.set_internal_state()
    # Wait for system to settle
    time.sleep(settling_time)

    predicted_x = np.array([])
    predicted_y = np.array([])
    measured_x = np.array([])
    measured_y = np.array([])

    ###########################################################
    gradient = np.linspace(0.0001, 2, x_points)
    inv_gradient = gradient[::-1]
    a = gradient
    b = inv_gradient
    c = inv_gradient
    d = gradient
    a_total = np.array([])
    b_total = np.array([])
    c_total = np.array([])
    d_total = np.array([])
    for index in np.linspace(-1, 1, y_points):  # number of Y samples
        offset = 1  # base power from the device
        a_total = np.append(a_total, (a + index) + offset)
        b_total = np.append(b_total, (b + index) + offset)
        c_total = np.append(c_total, (c - index) + offset)
        d_total = np.append(d_total, (d - index) + offset)
    #############################################################

    for a, b, c, d in zip(a_total, b_total, c_total, d_total):
        # Steps here go as follows:
        # - Take the four values given to the loop, and split them into ratios that will sum into 1
        # - Set a nominal attenuation on the attenuator, so amplification can be simulated if needed
        # - Read the power set by the RF and convert it from dB into mW, then divide it by 4 as this is what
        #   the splitter will do.
        # - Put each of the four power values through the nominal attenuation value of each channel, summing these
        #   values after will give the total power delivered into the BPM.
        # - The total power delivered into the BPM can then be multiplied by the ratios given in step 1 to
        #   calculate the desired power to be delivered into each BPM input.
        # - Converting these powers into dB with respect to the origional power delivered to the input, will give the
        #   change in dB value of each attenuator.

        abcd_total = a + b + c + d  # Sum the values given by the loop before
        a = a / abcd_total  # Normalise the A value into a ratio
        b = b / abcd_total  # Normalise the B value into a ratio
        c = c / abcd_total  # Normalise the C value into a ratio
        d = d / abcd_total  # Normalise the D value into a ratio

        prog_atten_object.set_global_attenuation(nominal_attenuation)  # sets nominal attenuation value on each channel
        power_total = rf_object.get_output_power()[0] # Gets the power output by the RF, total power into the system
        power_total = 10.0 ** (power_total / 10.0)  # converts power output from dBm into mW
        power_split = power_total / 4.0  # Divide the power by 4 as it goes through a four way splitter

        # Attenuation effect in decimal of the nominal attenuation value
        linear_nominal_attenuation = 10.0 ** (-nominal_attenuation / 10.0)
        # The power delivered into each BPM input after passing through the attenuator with nominal values
        # Assuming no losses through cables etc...
        # Set the power delivered into each BPM as this value
        power_split = power_split * linear_nominal_attenuation
        a_pwr = power_split
        b_pwr = power_split
        c_pwr = power_split
        d_pwr = power_split

        power_total = a_pwr + b_pwr + c_pwr + d_pwr  # Total power into the BPM after each signal is attenuated

        # Desired power into the each input, given their power ratio, and power delivered under nominal attenuation
        a_pwr = a * power_total
        b_pwr = b * power_total
        c_pwr = c * power_total
        d_pwr = d * power_total

        # Calculate new attenuation values by converting the ratio of desired power and previous power into dB
        # Then set the attenuation as the difference between this and the nominal attenuation value.
        a = nominal_attenuation - quarter_round(10*np.log10(a_pwr / power_split))
        b = nominal_attenuation - quarter_round(10*np.log10(b_pwr / power_split))
        c = nominal_attenuation - quarter_round(10*np.log10(c_pwr / power_split))
        d = nominal_attenuation - quarter_round(10*np.log10(d_pwr / power_split))

        # Set the attenuation as the values just calculated.
        prog_atten_object.set_channel_attenuation("A", a)
        prog_atten_object.set_channel_attenuation("B", b)
        prog_atten_object.set_channel_attenuation("C", c)
        prog_atten_object.set_channel_attenuation("D", d)

        ######################################
        time.sleep(settling_time)  # Let the attenuator values settle
        ######################################
        measured_x = np.append(measured_x, bpm_object.get_x_position())  # Take a reading of X position
        measured_y = np.append(measured_y, bpm_object.get_y_position())  # Take a reading of Y position
        # Given the power values of each input, calculate the expected position
        predicted_x = np.append(predicted_x, calc_x_pos(a_pwr, b_pwr, c_pwr, d_pwr))
        predicted_y = np.append(predicted_y, calc_y_pos(a_pwr, b_pwr, c_pwr, d_pwr))

    plt.plot(measured_x, measured_y, 'bo',
             predicted_x, predicted_y, 'r+', markersize=10,)
    plt.xlim(-10.5, 10.5)
    plt.ylim(-10.5, 10.5)

    plt.xlabel("Horizontal Beam Position (mm)")
    plt.ylabel("Vertical Beam Position (mm)")
    plt.grid(True)

    if report_object is None:
        # If no report is entered as an input to the test, simply display the results
        plt.show()
    else:
        # If there is a report for the data to be copied to, do so.

        # Readies text that will introduce this test in the report
        intro_text = r"""Moves the beam position to -5 to 5 in the XY plane and recods beam position.
        The calc\_x\_pos and calc\_y\_pos functions are used to measure the theoretical beam position values.
        A set of ABCD values are created that will move the beam position from -5 to 5 in both the X and Y
        plane. This is then converted into attenuation values to put into the attenuator. A fixed RF frequency 
        and power is used while the attenuator values are changed. Finally the predicted values are compared 
        with the measured values of position. \\~\\
        """
        # Readies devices that are used in the test so that they can be added to the report
        device_names = []
        device_names.append('RF source is ' + rf_object.get_device_id())
        device_names.append('BPM is ' + bpm_object.get_device_id())
        device_names.append('Attenuator is ' + prog_atten_object.get_device_id())
        # # Readies parameters that are used in the test so that they can be added to the report
        parameter_names = []
        parameter_names.append("Fixed RF Output Power: " + str(rf_power) + "dBm")
        parameter_names.append("Fixed Rf Output Frequency: " + str(rf_frequency) + "MHz")
        parameter_names.append("Nominal Attenuation: " + str(nominal_attenuation) + "dB")
        parameter_names.append("Number of X points: " + str(x_points))
        parameter_names.append("Nunber of Y points: " + str(y_points))
        parameter_names.append("Settling time: " + str(settling_time) + "s")

        plt.savefig(''.join((sub_directory, "Beam_position_equidistant_grid_raster_scan_test" + ".pdf")))
        report_object.setup_test(test_name, intro_text, device_names, parameter_names)
        report_object.add_figure_to_test(image_name=''.join((sub_directory,
                                                            "Beam_position_equidistant_grid_raster_scan_test")),
                                         caption="Beam_position_equidistant_grid_raster_scan_test")
        savemat(sub_directory+"beam_position_raster_scan_data" + ".mat",
                {'measured_x': measured_x,
                 'measured_y': measured_y,
                 'predicted_x': predicted_x,
                 'predicted_y': predicted_y})

