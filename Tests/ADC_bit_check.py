import numpy as np
import time
from scipy.io import savemat


def adc_test(
             test_system_object,
             rf_object,
             bpm_object,
             prog_atten_object,
             frequency,
             power_level=-20,
             settling_time=1,
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
    test_name = test_system_object.test_initialisation(__name__, rf_object, prog_atten_object, bpm_object,
                                                       frequency, power_level)
    bpm_object.set_internal_state(agc='AGC off',
                                  delta=0,
                                  offset=0,
                                  switches='Manual',
                                  switch_state=bpm_object.switch_straight,
                                  attenuation=0,
                                  dsc='Unity gains',
                                  ft_state='Enabled')
    # Wait for signal to settle
    time.sleep(settling_time)

    # Setting up variables.
    data = np.empty((1024, 16, bpm_object.num_adcs))
    data_std = np.empty((16, bpm_object.num_adcs))
    # data = np.empty((1024, bpm_object.adc_n_bits, bpm_object.num_adcs))
    # data_std = np.empty((bpm_object.adc_n_bits, bpm_object.num_adcs))

    # Gets 1024 samples for each ADC.
    time_tmp, data1_tmp, data2_tmp, data3_tmp, data4_tmp = bpm_object.get_adc_data(16)  # record data


    #  Converting to arrays of binary values
    # First convert the int value into a binary string.
    # Turn that sting into a list of values.
    # Then turn that list of lists into an array
    # This should be bpm_object.adc_n_bits in size. However if this is not 16 there is a broadcast error.
    # This is because the epics layer always returns a 16 bit number.
    # For now set to 16. The upper extra bits will be ignored in the later processing anyway.
    format_string = '0%db' % 16  # bpm_object.adc_n_bits
    # print data1_tmp
    # test = np.asarray([list(format(x, format_string)) for x in data1_tmp])
    # print test
    data[:, :, 0] = np.asarray([list(format(x, format_string)) for x in data1_tmp])
    data[:, :, 1] = np.asarray([list(format(x, format_string)) for x in data2_tmp])
    data[:, :, 2] = np.asarray([list(format(x, format_string)) for x in data3_tmp])
    data[:, :, 3] = np.asarray([list(format(x, format_string)) for x in data4_tmp])

    for kw in range(bpm_object.num_adcs):
        for wn in range(bpm_object.adc_n_bits):
            data_std[wn, kw] = np.std(data[:, wn, kw])

    print sub_directory
    savemat(''.join((sub_directory, 'ADC_bit_check', '_data.mat')),
            {'data': data,
             'data_std': data_std,
             'n_bits': bpm_object.adc_n_bits,
             'n_adc': bpm_object.num_adcs,
             'data_adc1': data1_tmp,
             'data_adc2': data2_tmp,
             'data_adc3': data3_tmp,
             'data_adc4': data4_tmp,
             'time': time_tmp,
             'bpm_agc': bpm_object.agc,
             'bpm_switching': bpm_object.switches,
             'bpm_dsc': bpm_object.dsc,
             'test_name': test_name,
             'rf_hw': test_system_object.rf_hw,
             'bpm_hw': test_system_object.bpm_hw})

    # turn off the RF
    rf_object.turn_off_RF()
