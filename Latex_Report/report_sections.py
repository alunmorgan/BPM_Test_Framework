import helper_functions
import Latex_Report
import os.path
import json
from helper_functions import pass_fail


def switching_state_label(switching_orig):
    if switching_orig == 1:
        switching = 'On'
    elif switching_orig == 0:
        switching = 'Off'
    else:
        raise ValueError('AGC value is incorrect')
    return switching


def agc_state_label(agc_orig):
    if agc_orig == 1:
        agc = 'On'
    elif agc_orig == 0:
        agc = 'Off'
    else:
        raise ValueError('AGC value is incorrect')
    return agc


def dsc_state_label(dsc_orig):
    if dsc_orig == 0:
        dsc = 'Fixed gains'
    elif dsc_orig == 1:
        dsc = 'Unity gains'
    elif dsc_orig == 2:
        dsc = 'Automatic'
    else:
        raise ValueError('DSC value is incorrect')
    return dsc


def assemble_report(subdirectory):

    report = Latex_Report.TexReport(subdirectory=subdirectory)

    if os.path.exists(os.path.join(subdirectory, 'ADC_bit_check_data.json')):
        report_section_adc_bit_test(report_object=report, subdirectory=subdirectory,
                                    test_data='ADC_bit_check_data.json')

    if os.path.exists(os.path.join(subdirectory, 'ADC_int_atten_sweep_data.json')):
        report_section_adc_int_atten(report_object=report, subdirectory=subdirectory,
                                     test_data='ADC_int_atten_sweep_data.json')

    if os.path.exists(os.path.join(subdirectory, 'beam_position_raster_scan_data.json')):
        report_section_position_raster_scan(report_object=report, subdirectory=subdirectory,
                                            test_data='beam_position_raster_scan_data.json')

    if os.path.exists(os.path.join(subdirectory, 'beam_power_dependence_data.json')):
        report_section_beam_power_dependence(report_object=report, subdirectory=subdirectory,
                                             test_data='beam_power_dependence_data.json',
                                             ref_data='initial_BPM_state.json')

    if os.path.exists(os.path.join(subdirectory, 'constant_fill_charge_fill_sweep_data.json')):
        report_section_fixed_voltage_amplitude_fill_pattern(report_object=report, subdirectory=subdirectory,
                                                            test_data='constant_fill_charge_fill_sweep_data.json')

    if os.path.exists(os.path.join(subdirectory, 'constant_bunch_charge_fill_sweep_data.json')):
        report_section_bunch_train_length_dependency(report_object=report, subdirectory=subdirectory,
                                                     test_data='constant_bunch_charge_fill_sweep_data.json')

    if os.path.exists(os.path.join(subdirectory, 'Noise_test_data.json')):
        report_section_noise_test(report_object=report, subdirectory=subdirectory,
                                  test_data=['Noise_test_data.json', 'Noise_test_data_complex.json'])

    report.create_report()


def report_section_adc_bit_test(report_object, subdirectory, test_data):
    with open(os.path.join(subdirectory, test_data), 'r') as read_data:
        loaded_data = json.load(read_data)
    test_limit = 0.05
    status_label, status = pass_fail.adc_bit_test_pass_fail(loaded_data=loaded_data, lim=test_limit)
    intro_text = r"""Excites with a sine wave and then gets the ADC data from each channel. 
     Plots the histogram to that any missing bits can be identified. The expected value is 0.5. 
     Any value 0.1 away from this indicates a problem.

     The RF signal is a sine wave.  \\~\\
     """
    # Get the device names for the report
    device_names = ['RF source is ' + loaded_data['rf_hw']]

    # Get the parameter values for the report
    parameter_names = ['AGC %s' % agc_state_label(loaded_data['bpm_agc']),
                       ''.join(('Switching ', switching_state_label(loaded_data['bpm_switching']))),
                       'DSC %s' % dsc_state_label(loaded_data['bpm_dsc']),
                       'BPM attenuation setting %s dB' % str(loaded_data['bpm_attenuation']),
                       'Test limit %s' % str(test_limit)
                       ]

    # add the test details to the report
    report_object.setup_test(' - '.join((loaded_data['test_name'], status_label)), intro_text, device_names, parameter_names)

    # make a caption and headings for a table of results
    caption = "ADC range rached by the RF signal"
    headings = [["ADC", "Max", "Min"],
                ["", "(counts)", "(counts)"]]
    data = [range(len(loaded_data['data']) + 1)[1:],
            [max(loaded_data['data'][x]) for x in range(len(loaded_data['data']))],
            [min(loaded_data['data'][x]) for x in range(len(loaded_data['data']))]]
    # copy the values to the report
    report_object.add_table_to_test('|c|c|c|', data, headings, caption)

    fig1_adc = helper_functions.plot_adc_bit_check_data(sub_directory=subdirectory,
                                                        loaded_data=loaded_data)
    report_object.add_figure_to_test(image_name=fig1_adc, caption='ADC bit test. All should be close to 0.5',
                                     fig_width=0.6)


def report_section_adc_int_atten(report_object, subdirectory, test_data):
    with open(os.path.join(subdirectory, test_data), 'r') as read_data:
        loaded_data = json.load(read_data)
    test_limit = 0.1
    status_label, status = pass_fail.internal_attenuator_pass_fail(loaded_data=loaded_data, lim=test_limit)
    intro_text = r"""The RF signal is a sine wave.
    As the external attenuation is reduced, the internal is increased to compensate. 
    The total attenuation remains the same.
    SA data from each channel is captured at each signal level. 
       \\~\\
     """
    # Get the device names for the report
    device_names = ['RF source is ' + loaded_data['rf_id'],
                    'Programmable attenuator is ' + loaded_data['prog_atten_id']]

    # Get the parameter values for the report
    parameter_names = ['Output power level: ' + str(
        helper_functions.round_to_2sf(loaded_data['output_power'])),
                       'AGC %s' % agc_state_label(loaded_data['bpm_agc']),
                       ''.join(('Switching ', switching_state_label(loaded_data['bpm_switching']))),
                       'DSC %s' % dsc_state_label(loaded_data['bpm_dsc']),
                       'BPM attenuation setting %s dB' % str(loaded_data['bpm_attenuation']),
                       'Test limit is %s (%s percent)' % (str(test_limit), str(test_limit*100))
                       ]
    # add the test details to the report
    report_object.setup_test(' - '.join((loaded_data['test_name'], status_label)), intro_text, device_names, parameter_names)
    fig1_name, fig2_name = helper_functions.plot_adc_int_atten_sweep_data(sub_directory=subdirectory,
                                                                          loaded_data=loaded_data)
    report_object.add_figure_to_test(image_name=fig1_name, caption='Varying internal attenuation', fig_width=0.5)
    report_object.add_figure_to_test(image_name=fig2_name, caption='Varying internal attenuation (normalised signals)',
                                     fig_width=0.5)


def report_section_beam_power_dependence(report_object, subdirectory, test_data, ref_data):
    with open(os.path.join(subdirectory, test_data), 'r') as read_data:
        loaded_data = json.load(read_data)
    test_limit = 100
    status_label, status = pass_fail.power_dependence_pass_fail(loaded_data=loaded_data, level=test_limit)
    intro_text = r"""Tests the relationship between power at the BPM inputs and values read from the BPM. 
       
       An RF signal is output, and then different parameters are measured from the BPM. 
       The signal is changed, and the measurements are repeated.  \\~\\
       """
    # Get the device names for the report
    device_names = ['RF source is ' + loaded_data['rf_id'],
                    'Programmable attenuator is ' + loaded_data['prog_atten_id']]
    # Get the parameter values for the report
    parameter_names = ["Frequency: " + str(loaded_data['frequency']) + "MHz", "Power levels requested: " + str(
        helper_functions.round_to_2sf(loaded_data['set_output_power_levels'])) + "dBm", "Power levels used: " + str(
        helper_functions.round_to_2sf(loaded_data['output_power_levels'])) + "dBm",
                       "Settling time: " + str(loaded_data['settling_time']) + "s",
                       'AGC %s' % agc_state_label(loaded_data['bpm_agc']),
                       ''.join(('Switching ', switching_state_label(loaded_data['bpm_switching']))),
                       'DSC %s' % dsc_state_label(loaded_data['bpm_dsc']),
                       'BPM attenuation setting %s dB' % str(loaded_data['bpm_attenuation']),
                       'Test limit %s um ' % str(test_limit)]
    # add the test details to the report
    report_object.setup_test(' - '.join((loaded_data['test_name'], status_label)), intro_text, device_names, parameter_names)
    # make a caption and headings for a table of results
    caption = "Beam Power Dependence Results"
    headings = [["Input Power", " mean X Position", "mean Y Position", "Std X", "Std Y"],
                ["(dBm)", "(um)", "(um)", "(nm)", "(nm)"]]
    x_pos_mean, x_pos_std = helper_functions.stat_dataset(loaded_data['x_pos_raw'])
    y_pos_mean, y_pos_std = helper_functions.stat_dataset(loaded_data['y_pos_raw'])
    x_pos_mean_scaled = list()
    x_pos_mean_scaled_abs = list()
    for xpm in x_pos_mean:
        x_pos_mean_scaled.append(xpm * 1e3)
        x_pos_mean_scaled_abs.append(abs(x_pos_mean_scaled[-1]))
    y_pos_mean_scaled = list()
    y_pos_mean_scaled_abs = list()
    for ypm in y_pos_mean:
        y_pos_mean_scaled.append(ypm * 1e3)
        y_pos_mean_scaled_abs.append(abs(y_pos_mean_scaled[-1]))
    x_pos_std_scaled = list()
    for xps in x_pos_std:
        x_pos_std_scaled.append(xps * 1e6)
    y_pos_std_scaled = list()
    for yps in y_pos_std:
        y_pos_std_scaled.append(yps * 1e6)
    data = [loaded_data['set_output_power_levels'],
            x_pos_mean_scaled, y_pos_mean_scaled,
            x_pos_std_scaled, y_pos_std_scaled]
    # copy the values to the report
    report_object.add_table_to_test('|c|c|c|c|c|', data, headings, caption)
    fig1_bpd, fig_noise_time, fig_noise_freq = helper_functions.plot_beam_power_dependence_data(
        sub_directory=subdirectory,
        loaded_data=loaded_data,
        ref_data=ref_data)
    report_object.add_figure_to_test(image_name=fig1_bpd, caption='Position errors as a function of input power',
                                     fig_width=0.5)


def report_section_bunch_train_length_dependency(report_object, subdirectory, test_data):
    with open(os.path.join(subdirectory, test_data), 'r') as read_data:
        loaded_data = json.load(read_data)
    intro_text = r"""
           Equivalent to keeping the bunch charge constant.
           This test imitates a fill pattern by modulation the RF signal with a square wave. The up time 
           of the square wave represents when a bunch goes passed, and the downtime the gaps between the 
           bunches. This test will take the pulse length in micro seconds, and then linearly step up the 
           duty cycle of the pulse, from 0.1 to 1. Readings on the BPM are then recorded as the duty cycle
           is changed. While the duty cycle is increased, the peak RF voltage increases, meaning that 
           the average power will be constant with duty cycle change. \\~\\
       """
    device_names = ['RF source is ' + str(loaded_data['rf_hw'])]
    #    device_names.append('Gate is ' + str(loaded_data['gate_hw']))

    # Get the parameter values for the report
    parameter_names = ["Frequency: " + str(loaded_data['frequency']),
                       "Maximum Power: " + str(loaded_data['max_power']) + "dBm",
                       "Pulse Period: " + str(loaded_data['pulse_period']),
                       "Settling time: " + str(loaded_data['settling_time']) + "s",
                       'AGC ' + agc_state_label(loaded_data['bpm_agc']),
                       'Switching ' + switching_state_label(loaded_data['bpm_switching']),
                       'DSC ' + dsc_state_label(loaded_data['bpm_dsc']),
                       'BPM attenuation setting %s dB' % str(loaded_data['bpm_attenuation'])]
    # add the test details to the report
    report_object.setup_test(loaded_data['test_name'], intro_text, device_names, parameter_names)
    # make a caption and headings for a table of results
    caption = "Changing gate duty cycle, with fixed RF amplitude "
    headings = [["Duty Cycle", "mean X Position", "mean Y Position", "Std X", "Std Y"],
                ["(0-1)", "(um)", "(um)", "(um)", "(um)"]]
    data = [loaded_data['duty_cycles'],
            loaded_data['x_pos_mean'], loaded_data['y_pos_mean'],
            loaded_data['x_pos_std'], loaded_data['y_pos_std']]
    # copy the values to the report
    report_object.add_table_to_test('|c|c|c|c|c|', data, headings, caption)
    fig_name = helper_functions.plot_scaled_voltage_amplitude_fill_pattern_data(sub_directory=subdirectory,
                                                                                loaded_data=loaded_data)
    report_object.add_figure_to_test(image_name=fig_name, caption=fig_name)


def report_section_fixed_voltage_amplitude_fill_pattern(report_object, subdirectory, test_data):
    with open(os.path.join(subdirectory, test_data), 'r') as read_data:
        loaded_data = json.load(read_data)
    intro_text = r"""
           Equivalent to keeping the total charge in the train constant.
           This test imitates a fill pattern by modulation the RF signal with a square wave. The up time 
           of the square wave represents when a bunch goes passed, and the downtime the gaps between the 
           bunches. This test will take the pulse length in micro seconds, and then linearly step up the 
           duty cycle of the pulse, from 0.1 to 1. Readings on the BPM are then recorded as the duty cycle
           is changed. While the duty cycle is increased, the peak RF voltage stays fixed, meaning that 
           the average power will change with duty cycle. \\~\\
       """

    device_names = ['RF source is ' + str(loaded_data['rf_hw']), 'Gate is ' + str(loaded_data['gate_hw'])]
    # Get the parameter values for the report
    parameter_names = ["Frequency: " + str(loaded_data['frequency']), "Output Power: " + str(
        helper_functions.round_to_2sf(loaded_data['max_power'])) + "dBm",
                       "Pulse Period: " + str(loaded_data['pulse_period']),
                       "Settling time: " + str(loaded_data['settling_time']) + "s",
                       'AGC ' + str(loaded_data['bpm_agc']), 'Switching ' + str(loaded_data['bpm_switching']),
                       'DSC %s' % dsc_state_label(loaded_data['bpm_dsc']),
                       'BPM attenuation setting %s dB' % str(loaded_data['bpm_attenuation'])]
    # add the test details to the report
    report_object.setup_test(loaded_data['test_name'], intro_text, device_names, parameter_names)

    # make a caption and headings for a table of results
    caption = "Changing gate duty cycle, with fixed RF amplitude "
    headings = [["Duty Cycle", "mean X Position", "mean Y Position", "Std X", "Std Y"],
                ["(0-1)", "(um)", "(um)", "(um)", "(um)"]]
    data = [loaded_data['duty_cycles'],
            loaded_data['x_pos_mean'], loaded_data['y_pos_mean'],
            loaded_data['x_pos_std'], loaded_data['y_pos_std']]

    # copy the values to the report
    report_object.add_table_to_test('|c|c|c|c|c|', data, headings, caption)
    fig_name = helper_functions.plot_fixed_voltage_amplitude_fill_pattern_data(sub_directory=subdirectory,
                                                                               loaded_data=loaded_data)
    report_object.add_figure_to_test(image_name=fig_name, caption=fig_name)


def report_section_position_raster_scan(report_object, subdirectory, test_data):
    with open(os.path.join(subdirectory, test_data), 'r') as read_data:
        loaded_data = json.load(read_data)
    test_limit = 0.05
    status_label, status, test_results = pass_fail.raster_scan_pass_fail(loaded_data=loaded_data, lim=test_limit)
    centre_test_limit = 0.03
    centre_status_label, centre_status, centre_test_results = pass_fail.centre_offset_pass_fail(loaded_data=loaded_data, lim=centre_test_limit)
    # Readies text that will introduce this test in the report
    intro_text = r"""Moves the beam position in the XY plane and records beam position.
             A fixed RF frequency and power is used while the attenuator values are changed. 
             Finally the predicted values are compared with the measured values of position. \\~\\
            """
    # Readies devices that are used in the test so that they can be added to the report
    device_names = ['RF source is ' + loaded_data['rf_id'], 'Attenuator is ' + loaded_data['prog_atten_id']]
    # # Readies parameters that are used in the test so that they can be added to the report
    parameter_names = ["Power at BPM input: " + str(
        helper_functions.round_to_2sf(loaded_data['output_power_level'])) + "dBm",
                       "Fixed RF Output Frequency: " + str(loaded_data['frequency']) + "MHz",
                       "Number of repeat points: " + str(len(loaded_data['measured_x'])),
                       "Settling time: " + str(loaded_data['settling_time']) + "s",
                       'AGC ' + agc_state_label(loaded_data['bpm_agc']),
                       'Switching ' + switching_state_label(loaded_data['bpm_switching']),
                       'DSC ' + dsc_state_label(loaded_data['bpm_dsc']),
                       'BPM attenuation setting %s dB' % str(loaded_data['bpm_attenuation']),
                       'Scan test limit %s (%s um)' % (test_limit, test_limit * 1000),
                       'Centre test limit %s (%s um)' % (centre_test_limit, centre_test_limit * 1000)]

    report_object.setup_test(' '.join((loaded_data['test_name'], '-scan', status_label, '-centre', centre_status_label)), intro_text, device_names, parameter_names)

    fig_name = helper_functions.plot_raster_scan(subdirectory, loaded_data, test_results, centre_test_results)

    report_object.add_figure_to_test(image_name=fig_name, caption="Beam position equidistant grid raster scan test")


def report_section_noise_test(report_object, subdirectory, test_data):
    with open(os.path.join(subdirectory, test_data[0]), 'r') as read_data:
        loaded_data = json.load(read_data)
    with open(os.path.join(subdirectory, test_data[1]), 'r') as read_data_complex:
        loaded_data_complex = json.load(read_data_complex)
    intro_text = r"""Compares the noise generated.

        In order to get the baseline, the RF signal is turned off, and then different parameters 
        are measured from the BPM.  \\~\\
        The BPM input power is then set to different values and the measurements are repeated.
        The mean values of the captured data are plotted, with the Baseline placed at -100dBm.\\~\\
        """
    # Get the device names for the report
    device_names = ['RF source is ' + loaded_data['rf_id'],
                    'Programmable attenuator is ' + loaded_data['prog_atten_id']]
    # Get the parameter values for the report
    parameter_names = ["power levels: " + str(
        helper_functions.round_to_2sf(loaded_data['output_power_levels']))]
    # add the test details to the report
    report_object.setup_test(loaded_data['test_name'], intro_text, device_names, parameter_names)
    # make a caption and headings for a table of results
    # caption = "Noise Results"
    # headings = [["X Position", "Y Position", ], ["(mm)", "(mm)"]]
    # data = [x_pos_baseline, y_pos_baseline]
    # copy the values to the report
    # report_object.add_table_to_test('|c|c|', data, headings, caption)
    fig_names = helper_functions.plot_noise(subdirectory, loaded_data, loaded_data_complex)

    for fig_n in fig_names:
        head, tail = os.path.split(fig_n)
        report_object.add_figure_to_test(image_name=fig_n, caption=tail)
