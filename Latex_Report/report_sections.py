from scipy.io import loadmat
import plotting_helper_functions
import Latex_Report


def assemble_report(subdirectory):
    bpm_state = loadmat(''.join((subdirectory, 'initial_BPM_state.mat')))
    report = Latex_Report.Tex_Report('/'.join((subdirectory, "BPMTestReport")), bpm_state['mac_address'][0])
    report_section_adc_bit_test(report_object=report, subdirectory=subdirectory, test_data='ADC_bit_check_data.mat')
    report_section_adc_int_atten(report_object=report, subdirectory=subdirectory, test_data='ADC_int_atten_sweep_data.mat')
    #report_section_beam_power_dependence(report_object=report, subdirectory=subdirectory, test_data='beam_power_dependence_data.mat')
    #report_section_fixed_voltage_amplitude_fill_pattern(report_object=report, subdirectory=subdirectory, test_data='constant_fill_charge_fill_sweep_data.mat')
    #report_section_scaled_voltage_amplitude_fill_pattern(report_object=report, subdirectory=subdirectory, test_data='constant_bunch_charge_fill_sweep_data.mat')
    report.create_report()


def report_section_adc_bit_test(report_object, subdirectory, test_data):
    loaded_data = loadmat(''.join((subdirectory, test_data)))
    intro_text = r"""Excites with a sine wave and then gets the ADC data from each channel. 
     Plots the histogram to that any missing bits can be identified. The expected value is 0.5. 
     Any value 0.1 away from this indicates a problem.

     The RF signal is a sine wave.  \\~\\
     """
    # Get the device names for the report
    device_names = []
    device_names.append('RF source is ' + loaded_data['rf_hw'][0])
    device_names.append('BPM is ' + loaded_data['bpm_hw'][0])

    # Get the parameter values for the report
    dsc_orig = loaded_data['bpm_dsc'][0][0][1][0][0]
    if dsc_orig == 0:
        dsc = 'Fixed gains'
    elif dsc_orig == 1:
        dsc = 'Unity gains'
    elif dsc_orig == 2:
        dsc = 'Automatic'
    else:
        raise ValueError('DSC value is incorrect')

    parameter_names = []
    parameter_names.append('AGC %d' % loaded_data['bpm_agc'][0][0][1][0][0])
    parameter_names.append('Switching %d' % loaded_data['bpm_switching'][0][0][1][0][0])
    parameter_names.append('DSC %s' % dsc)

    # add the test details to the report
    report_object.setup_test(loaded_data['test_name'][0], intro_text, device_names, parameter_names)
    plotting_helper_functions.plot_adc_bit_check_data(report_object=report_object,
                                                      sub_directory=subdirectory,
                                                      input_file=test_data)


def report_section_adc_int_atten(report_object, subdirectory, test_data):
    loaded_data = loadmat(''.join((subdirectory, test_data)))
    intro_text = r"""Excites with different signal levels. Gets the ADC data from each channel at each signal level. 
     Plots the curve.

     The RF signal is a sine wave.  \\~\\
     """
    # Get the device names for the report
    device_names = []
    #device_names.append('RF source is ' + loaded_data['rf_hw'][0])
    #device_names.append('BPM is ' + loaded_data['bpm_hw'][0])

    # Get the parameter values for the report
    parameter_names = []
    parameter_names.append('Attenuation levels: ' + str(loaded_data['attenuation'][0]))
    # add the test details to the report
    report_object.setup_test(loaded_data['test_name'][0], intro_text, device_names, parameter_names)
    plotting_helper_functions.plot_adc_int_atten_sweep_data(report_object=report_object,
                                                            sub_directory=subdirectory,
                                                            input_file=test_data)


def report_section_beam_power_dependence(report_object, subdirectory, test_data):
    loaded_data = loadmat(''.join((subdirectory, test_data)))
    intro_text = r"""Tests the relationship between RF output power and values read from the BPM. 
       An RF signal is output, and then different parameters are measured from the BPM. 
       The signal is linearly ramped up in dBm at a single frequency. The number of samples to take, 
       and settling time between each measurement can be decided using the arguments. \\~\\
       """
    # Get the device names for the report
    device_names = []
    device_names.append('RF source is ' + loaded_data['rf_hw'][0])
    device_names.append('BPM is ' + loaded_data['bpm_hw'][0])
    # Get the parameter values for the report
    # Get the parameter values for the report
    dsc_orig = loaded_data['bpm_dsc'][0][0][1][0][0]
    if dsc_orig == 0:
        dsc = 'Fixed gains'
    elif dsc_orig == 1:
        dsc = 'Unity gains'
    elif dsc_orig == 2:
        dsc = 'Automatic'
    else:
        raise ValueError('DSC value is incorrect')
    parameter_names = []
    parameter_names.append("Frequency: " + str(loaded_data['frequency'][0]) + "MHz")
    parameter_names.append("Power levels used: " + str(loaded_data['power_levels'][0]) + "dBm")
    parameter_names.append("Settling time: " + str(loaded_data['settling_time'][0]) + "s")
    parameter_names.append('AGC %d' % loaded_data['bpm_agc'][0][0][1][0][0])
    parameter_names.append('Switching %d' % loaded_data['bpm_switching'][0][0][1][0][0])
    parameter_names.append('DSC %s' % dsc)
    # add the test details to the report
    report_object.setup_test(loaded_data['test_name'][0], intro_text, device_names, parameter_names)
    # make a caption and headings for a table of results
    caption = "Beam Power Dependence Results"
    headings = [["Input Power", " mean X Position", "mean Y Position", "Std X", "Std Y"],
                ["(dBm)", "(um)", "(um)", "(um)", "(um)"]]
    data = [loaded_data['input_power'][0],
            loaded_data['x_pos_mean'][0], loaded_data['y_pos_mean'][0],
            loaded_data['x_pos_std'][0], loaded_data['y_pos_std'][0]]
    # copy the values to the report
    report_object.add_table_to_test('|c|c|c|c|c|', data, headings, caption)
    plotting_helper_functions.plot_beam_power_dependence_data(report_object=report_object,
                                                              sub_directory=subdirectory,
                                                              input_file=test_data)


def report_section_scaled_voltage_amplitude_fill_pattern(report_object, subdirectory, test_data):
    loaded_data = loadmat(''.join((subdirectory, test_data)))
    intro_text = r"""
           Equivalent to keeping the bunch charge constant.
           This test imitates a fill pattern by modulation the RF signal with a square wave. The up time 
           of the square wave represents when a bunch goes passed, and the downtime the gaps between the 
           bunches. This test will take the pulse length in micro seconds, and then linearly step up the 
           duty cycle of the pulse, from 0.1 to 1. Readings on the BPM are then recorded as the duty cycle
           is changed. While the duty cycle is increased, the peak RF voltage increases, meaning that 
           the average power will be constant with duty cycle change. \\~\\
       """
    device_names = []
    device_names.append('RF source is ' + loaded_data['rf_hw'][0])
    device_names.append('BPM is ' + loaded_data['bpm_hw'][0])
    device_names.append('Gate is ' + loaded_data['gate_hw'][0])

    # Get the parameter values for the report
    dsc_orig = loaded_data['bpm_dsc'][0][0][1][0][0]
    if dsc_orig == 0:
        dsc = 'Fixed gains'
    elif dsc_orig == 1:
        dsc = 'Unity gains'
    elif dsc_orig == 2:
        dsc = 'Automatic'
    else:
        raise ValueError('DSC value is incorrect')
    parameter_names = []
    parameter_names.append("Frequency: " + loaded_data['frequency'][0][1])
    parameter_names.append("Maximum Power: " + str(loaded_data['max_power'][0]) + "dBm")
    parameter_names.append("Pulse Period: " + loaded_data['pulse_period'][0][1])
    parameter_names.append("Settling time: " + str(loaded_data['settling_time'][0]) + "s")
    parameter_names.append('AGC %d' % loaded_data['bpm_agc'][0])
    parameter_names.append('Switching %d' % loaded_data['bpm_switching'][0])
    parameter_names.append('DSC %s' % dsc)
    # add the test details to the report
    report_object.setup_test(loaded_data['test_name'][0], intro_text, device_names, parameter_names)
    # make a caption and headings for a table of results
    caption = "Changing gate duty cycle, with fixed RF amplitude "
    headings = [["Duty Cycle", "mean X Position", "mean Y Position", "Std X", "Std Y"],
                ["(0-1)", "(um)", "(um)", "(um)", "(um)"]]
    data = [loaded_data['duty_cycles'][0],
            loaded_data['x_pos_mean'][0], loaded_data['y_pos_mean'][0],
            loaded_data['x_pos_std'][0], loaded_data['y_pos_std'][0]]
    # copy the values to the report
    report_object.add_table_to_test('|c|c|c|c|c|', data, headings, caption)
    plotting_helper_functions.plot_scaled_voltage_amplitude_fill_pattern_data(report_object=report_object,
                                                                              sub_directory=subdirectory,
                                                                              input_file=test_data)


def report_section_fixed_voltage_amplitude_fill_pattern(report_object, subdirectory, test_data):
    loaded_data = loadmat(''.join((subdirectory, test_data)))
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
    device_names.append('RF source is ' + loaded_data['rf_hw'][0])
    device_names.append('BPM is ' + loaded_data['bpm_hw'][0])
    device_names.append('Gate is ' + loaded_data['gate_hw'][0])
    # Get the parameter values for the report
    dsc_orig = loaded_data['bpm_dsc'][0][0][1][0][0]
    if dsc_orig == 0:
        dsc = 'Fixed gains'
    elif dsc_orig == 1:
        dsc = 'Unity gains'
    elif dsc_orig == 2:
        dsc = 'Automatic'
    else:
        raise ValueError('DSC value is incorrect')
    parameter_names = []
    parameter_names.append("Frequency: " + loaded_data['frequency'][0][1])
    parameter_names.append("Output Power: " + str(loaded_data['max_power'][0]) + "dBm")
    parameter_names.append("Pulse Period: " + loaded_data['pulse_period'][0][1])
    parameter_names.append("Settling time: " + str(loaded_data['settling_time'][0]) + "s")
    parameter_names.append('AGC %d' % loaded_data['bpm_agc'][0])
    parameter_names.append('Switching %d' % loaded_data['bpm_switching'][0])
    parameter_names.append('DSC %s' % dsc)
    # add the test details to the report
    report_object.setup_test(loaded_data['test_name'][0], intro_text, device_names, parameter_names)

    # make a caption and headings for a table of results
    caption = "Changing gate duty cycle, with fixed RF amplitude "
    headings = [["Duty Cycle", "mean X Position", "mean Y Position", "Std X", "Std Y"],
                ["(0-1)", "(um)", "(um)", "(um)", "(um)"]]
    data = [loaded_data['duty_cycles'][0],
            loaded_data['x_pos_mean'][0], loaded_data['y_pos_mean'][0],
            loaded_data['x_pos_std'][0], loaded_data['y_pos_std'][0]]

    # copy the values to the report
    report_object.add_table_to_test('|c|c|c|c|c|', data, headings, caption)
    plotting_helper_functions.plot_fixed_voltage_amplitude_fill_pattern_data(report_object=report_object,
                                                                             sub_directory=subdirectory,
                                                                             input_file=test_data)
