import numpy as np
import time
from scipy.io import savemat


def beam_power_dependence(
                          test_system_object,
                          rf_object,
                          bpm_object,
                          prog_atten_object,
                          frequency,
                          power_levels=range(-40, -100, -10),
                          settling_time=1,
                          samples=10,
                          sub_directory=""):
    """Tests the relationship between RF output power and values read from the BPM.

    An RF signal is output, and then different parameters are measured from the BPM. 
    The signal is linearly ramped up in dBm at a single frequency. The number of samples to take, 
    and settling time between each measurement can be decided using the arguments. 

    Args:
        test_system_object (System Obj): Object capturing the system losses and hardware ids.
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
        samples (int): The number of samples to capture at each data point.
        report_object (LaTeX Report Obj): Specific report that the test results will be recorded
            to. If no report is sent to the test then it will just display the results in 
            a graph. 
        sub_directory (str): String that can change where the graphs will be saved to.

    Returns:
        float array: Power read at the BPM
        float array: X Positions read from the BPM
        float array: Y Positions read from the BPM
        float array: Standard deviation of X Positions read from the BPM
        float array: Standard deviation Y Positions read from the BPM
    """

    test_name = test_system_object.test_initialisation(__name__, rf_object, prog_atten_object,
                                                       bpm_object, frequency, power_levels[0])
    # Wait for signal to settle
    time.sleep(settling_time)
    # Set up BPM for normal operation
    bpm_object.set_internal_state(agc=0, attenuation=35)

    # Build up the arrays where the final values will be saved
    x_pos_raw = np.array([])
    y_pos_raw = np.array([])
    x_pos_mean = np.array([])
    y_pos_mean = np.array([])
    x_pos_std = np.array([])
    y_pos_std = np.array([])
    input_power = np.array([])

    # Perform the test
    for index in power_levels:
        # Set attenuator value to give desired power level.
        # As this is a relative adjustment the initial correction for system loss is
        # still valid.
        prog_atten_object.set_global_attenuation(power_levels[0] - index)
        time.sleep(settling_time)  # Wait for signal to settle

        # Perform the test
        x_time, x_pos_data = bpm_object.get_x_sa_data(samples)  # record X pos
        y_time, y_pos_data = bpm_object.get_y_sa_data(samples)  # record Y pos
        x_pos_raw = np.append(x_pos_raw, x_pos_data)
        y_pos_raw = np.append(y_pos_raw, y_pos_data)
        if index == power_levels[0]:
            x_pos_first = np.mean(x_pos_data)
            y_pos_first = np.mean(y_pos_data)
            x_pos_mean = [0]
            y_pos_mean = [0]
        else:
            x_pos_mean = np.append(x_pos_mean, (np.mean(x_pos_data) - x_pos_first) * 1e3)  # record X pos
            y_pos_mean = np.append(y_pos_mean, (np.mean(y_pos_data) - y_pos_first) * 1e3)  # record Y pos
        x_pos_std = np.append(x_pos_std, abs(np.std(x_pos_data)) * 1e3)  # record X pos
        y_pos_std = np.append(y_pos_std, abs(np.std(y_pos_data)) * 1e3)  # record Y pos
        input_power = np.append(input_power, bpm_object.get_input_power())

    savemat(sub_directory + "beam_power_dependence_data" + ".mat",
            {'input_power': input_power,
             'x_pos_raw': x_pos_raw,
             'x_pos_mean': x_pos_mean,
             'x_pos_std': x_pos_std,
             'y_pos_raw': y_pos_raw,
             'y_pos_mean': y_pos_mean,
             'y_pos_std': y_pos_std,
             'bpm_agc': bpm_object.agc,
             'bpm_switching': bpm_object.switches,
             'bpm_dsc': bpm_object.dsc,
             'test_name': test_name,
             'rf_hw': test_system_object.rf_hw,
             'bpm_hw': test_system_object.bpm_hw,
             'settling_time': settling_time,
             'frequency': frequency,
             'power_levels': power_levels})

    # turn off the RF
    rf_object.turn_off_RF()
