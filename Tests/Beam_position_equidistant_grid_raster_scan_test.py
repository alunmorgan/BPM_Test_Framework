from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
require("scipy")
import numpy as np
import time
from math import log10
import json


def beam_position_equidistant_grid_raster_scan_test(
                                                    test_system_object,
                                                    output_power_level,
                                                    rf_frequency,
                                                    x_points,
                                                    y_points,
                                                    settling_time,
                                                    sub_directory=""):
    """Moves the beam position to -5 to 5 in the XY plane and recods beam position

    The calc_x_pos and calc_y_pos functions are used to measure the theoretical beam position values.
    A set of ABCD values are created that will move the beam position from -5 to 5 in both the X and Y
    plane. This is then converted into attenuation values to put into the attenuator. A fixed RF frequency 
    and power is used while the attenuator values are changed. Finally the predicted values are compared 
    with the measured values of position. 

        Args:
            test_system_object (Obj): Object to set up the initial test conditions.
            output_power_level (float): Output power of the RF system throughout the test, in dBm
            rf_frequency (float): Frequency output of the RF throughout the test, in MHz
            x_points (int): number of samples in the X plane
            y_points (int) number of samples in the Y plane 
            settling_time (float): time in seconds to wait between changing an attenuator value and 
                taking a reading from the BPM.
            sub_directory (str): String that can change where the graphs will be saved to
                
        Returns:
            float list: measured X values of position
            float list: measured Y values of position
            float list: predicted X values of position
            float list: predicted Y values of position
    """
    # Initialise test
    test_name = test_system_object.test_initialisation(test_name=__name__,
                                                       frequency=rf_frequency,
                                                       output_power_level=output_power_level)
    # Set up BPM for normal operation
    test_system_object.BPM.set_internal_state({'agc': 0, 'attenuation': 35})
    bpm_input_power = test_system_object.BPM.get_input_power()
    test_system_object.RF.turn_on_RF()
    # Wait for system to settle
    time.sleep(settling_time)

    starting_attenuations = test_system_object.ProgAtten.get_global_attenuation()
    map_atten_bpm = test_system_object.channel_map

    beam_signal_x = np.linspace(-1, 1, x_points)
    beam_signal_y = np.linspace(-1, 1, y_points)
    beam_signal_sum = 1
    beam_signal_q = 0
    measured_x = []
    measured_y = []
    predicted_x = []
    predicted_y = []
    requested_x = []
    requested_y = []
    a = []
    b = []
    c = []
    d = []
    a_adj = []
    b_adj = []
    c_adj = []
    d_adj = []
    a_atten = []
    b_atten = []
    c_atten = []
    d_atten = []
    a_atten_readback = []
    b_atten_readback = []
    c_atten_readback = []
    d_atten_readback = []

    for x_index in beam_signal_x:
        for y_index in beam_signal_y:
            x_scaled = x_index  # / (test_system_object.BPM.kx * 0.1) #Kx is in mm?
            y_scaled = y_index  #/ (test_system_object.BPM.ky * 0.1) #Kx is in mm?

            a.append(beam_signal_sum/4. * (x_scaled + y_scaled + beam_signal_q + 1.))  # in V?
            b.append(beam_signal_sum/4. * (-x_scaled + y_scaled - beam_signal_q + 1.))  # in V?
            c.append(beam_signal_sum/4. * (-x_scaled - y_scaled + beam_signal_q + 1.)) # in V?
            d.append(beam_signal_sum/4. * (x_scaled - y_scaled - beam_signal_q + 1.))  # in V?

            if a[-1] > 0. and b[-1] > 0. and c[-1] > 0. and d[-1] > 0.:
                a_adj.append(log10(a[-1] / 0.25))
                b_adj.append(log10(b[-1] / 0.25))
                c_adj.append(log10(c[-1] / 0.25))
                d_adj.append(log10(d[-1] / 0.25))

                a_atten.append(starting_attenuations[map_atten_bpm['A'] - 1] - a_adj[-1])
                b_atten.append(starting_attenuations[map_atten_bpm['B'] - 1] - b_adj[-1])
                c_atten.append(starting_attenuations[map_atten_bpm['C'] - 1] - c_adj[-1])
                d_atten.append(starting_attenuations[map_atten_bpm['D'] - 1] - d_adj[-1])

                test_system_object.ProgAtten.set_channel_attenuation(map_atten_bpm['A'], a_atten[-1])
                test_system_object.ProgAtten.set_channel_attenuation(map_atten_bpm['B'], b_atten[-1])
                test_system_object.ProgAtten.set_channel_attenuation(map_atten_bpm['C'], c_atten[-1])
                test_system_object.ProgAtten.set_channel_attenuation(map_atten_bpm['D'], d_atten[-1])
                time.sleep(settling_time)

                a_atten_readback.append(test_system_object.ProgAtten.get_channel_attenuation(map_atten_bpm['A']))
                b_atten_readback.append(test_system_object.ProgAtten.get_channel_attenuation(map_atten_bpm['B']))
                c_atten_readback.append(test_system_object.ProgAtten.get_channel_attenuation(map_atten_bpm['C']))
                d_atten_readback.append(test_system_object.ProgAtten.get_channel_attenuation(map_atten_bpm['D']))

                measured_x.append(test_system_object.BPM.get_x_position())
                measured_y.append(test_system_object.BPM.get_y_position())
                requested_x.append(x_scaled)
                requested_y.append(y_scaled)

    test_system_object.RF.turn_off_RF()

    data_out = {'test_name': test_name,
                'rf_id': test_system_object.rf_id,
                'bpm_id': test_system_object.bpm_id,
                'rf_hw': test_system_object.rf_hw,
                'bpm_hw': test_system_object.bpm_hw,
                'prog_atten_id': test_system_object.prog_atten_id,
                'frequency': rf_frequency,
                'settling_time': settling_time,
                'output_power_level': output_power_level,
                'bpm_input_power': int(round(bpm_input_power)),
                'bpm_agc': test_system_object.BPM.agc,
                'bpm_switching': test_system_object.BPM.switches,
                'bpm_dsc': test_system_object.BPM.dsc,
                'measured_x': measured_x,
                'measured_y': measured_y,
                'requested_x': requested_x,
                'requested_y': requested_y,
                'predicted_x': predicted_x,
                'predicted_y': predicted_y,
                'a': a,
                'a_adj': a_adj,
                'a_atten': a_atten,
                'a_atten_readback': a_atten_readback,
                'b': b,
                'b_adj': b_adj,
                'b_atten': b_atten,
                'b_atten_readback': b_atten_readback,
                'c': c,
                'c_adj': c_adj,
                'c_atten': c_atten,
                'c_atten_readback': c_atten_readback,
                'd': d,
                'd_adj': d_adj,
                'd_atten': d_atten,
                'd_atten_readback': d_atten_readback,
                'starting_attenuations': starting_attenuations,
                'map_atten_bpm': map_atten_bpm
                }

    with open(sub_directory + "beam_position_raster_scan_data.json", 'w') as write_file:
        json.dump(data_out, write_file)






