import numpy as np
import time
import json
#  from scipy.io import savemat


def fixed_voltage_amplitude_fill_pattern_test(
                                   test_system_object,
                                   frequency,
                                   max_power=-40,
                                   duty_cycles=np.arange(1, 0, -0.1),
                                   pulse_period=1.87319,
                                   settling_time=1,
                                   samples=10,
                                   sub_directory=""):
    """
        This test imitates a fill pattern by modulation the RF signal with a square wave. The up time 
        of the square wave represents when a bunch goes passed, and the downtime the gaps between the 
        bunches. This test will take the pulse length in micro seconds, and then linearly step up the 
        duty cycle of the pulse, from 0.1 to 1. Readings on the BPM are then recorded as the duty cycle
        is changed. While the duty cycle is increased, the peak RF voltage stays fixed, meaning that 
        the average power will change with duty cycle. 
        

        Args:
            test_system_object (System Obj): Object capturing the devices used, system losses and hardware ids.
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

    """
    test_name = test_system_object.test_initialisation(test_name=__name__,
                                                       frequency=frequency,
                                                       power_level=max_power)
    if test_system_object.GS is not None:
        test_system_object.GS.set_pulse_period(pulse_period)
        test_system_object.GS.turn_on_modulation()
        test_system_object.GS.set_pulse_dutycycle(duty_cycles[0])
    # Set up BPM for normal operation
    test_system_object.BPM.set_internal_state({'agc': 0, 'attenuation': 35})
    test_system_object.RF.turn_on_RF()
    # Wait for system to settle
    time.sleep(5)

    # Build up the arrays where the final values will be saved
    x_pos_raw = np.array([])
    y_pos_raw = np.array([])
    x_pos_mean = np.array([])
    y_pos_mean = np.array([])
    x_pos_std = np.array([])
    y_pos_std = np.array([])

    for index in duty_cycles:
        if test_system_object.GS is not None:
            test_system_object.GS.set_pulse_dutycycle(index)
        time.sleep(settling_time)
        x_time, x_pos_data = test_system_object.BPM.get_x_sa_data(samples)  # record X pos
        y_time, y_pos_data = test_system_object.BPM.get_y_sa_data(samples)  # record Y pos
        x_pos_raw = np.append(x_pos_raw, x_pos_data)
        y_pos_raw = np.append(y_pos_raw, y_pos_data)
        if index == duty_cycles[0]:
            x_pos_first = np.mean(x_pos_data)
            y_pos_first = np.mean(y_pos_data)
            x_pos_mean = [0]
            y_pos_mean = [0]
        else:
            x_pos_mean = np.append(x_pos_mean, (np.mean(x_pos_data) - x_pos_first) * 1e3)  # record X pos
            y_pos_mean = np.append(y_pos_mean, (np.mean(y_pos_data) - y_pos_first) * 1e3)  # record Y pos
        x_pos_std = np.append(x_pos_std, np.std(x_pos_data) * 1e3)  # record X pos
        y_pos_std = np.append(y_pos_std, np.std(y_pos_data) * 1e3)  # record Y pos

    if test_system_object.gate_id is None:
        gate = ''
    else:
        gate = test_system_object.gate_id

    test_system_object.RF.turn_off_RF()
    if test_system_object.GS is not None:
        test_system_object.GS.turn_off_modulation()

    data_out = {'duty_cycles': list(duty_cycles),
                'x_pos_raw': list(x_pos_raw),
                'x_pos_mean': list(x_pos_mean),
                'x_pos_std': list(x_pos_std),
                'y_pos_raw': list(y_pos_raw),
                'y_pos_mean': list(y_pos_mean),
                'y_pos_std': list(y_pos_std),
                'bpm_agc': test_system_object.BPM.agc,
                'bpm_switching': test_system_object.BPM.switches,
                'bpm_dsc': test_system_object.BPM.dsc,
                'settling_time': settling_time,
                'frequency': frequency,
                'test_name': test_name,
                'rf_hw': test_system_object.rf_id,
                'bpm_hw': test_system_object.bpm_id,
                'gate_hw': gate,
                'max_power': max_power,
                'pulse_period': pulse_period}

    with open(sub_directory + "constant_fill_charge_fill_sweep_data.json", 'w') as write_file:
        json.dump(data_out, write_file)