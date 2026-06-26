import sys
import os
import time
import Test_system_common
import Latex_Report
import Tests
import json
from pkg_resources import require
require("numpy == 1.13.1")
require("scipy == 1.2.3")


def tests_for_single_bpm(test_sys, data_location, rf_frequency, settling_time=0.1):
    root_path = '/'.join((data_location, test_sys.BPM.mac_address.replace(':', '-'), time.strftime("%d-%m-%Y_T_%H-%M")))
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    subdirectory = ''.join((root_path, '/'))

    data_out = {'epics_id': test_sys.BPM.epics_id,
                'rf_id': test_sys.rf_id,
                'prog_atten_id': test_sys.prog_atten_id,
                'mac_address': test_sys.BPM.mac_address,
                'first_turn': test_sys.BPM.ft,
                'agc': test_sys.BPM.agc,
                'delta': test_sys.BPM.delta,
                'switches': test_sys.BPM.switches,
                'switch_val': test_sys.BPM.switch_val,
                'attenuation': test_sys.BPM.attn,
                'dsc': test_sys.BPM.dsc,
                'kx': test_sys.BPM.kx,
                'ky': test_sys.BPM.ky,
                'bpm_spec': test_sys.BPM.spec}

    with open(subdirectory + "initial_BPM_state.json", 'w') as write_file:
        json.dump(data_out, write_file)

    Tests.adc_test(test_system_object=test_sys,
                    frequency=rf_frequency,
                    output_power_level=-4,
                    settling_time=settling_time,
                    sub_directory=subdirectory
                    )

    Tests.adc_int_atten_sweep_test(test_system_object=test_sys,
                                    frequency=rf_frequency,
                                    output_power_level=-24,
                                    settling_time=settling_time,
                                    sub_directory=subdirectory)

    Tests.beam_power_dependence(test_system_object=test_sys,
                                frequency=rf_frequency,
                                output_power_levels=range(-4, -50, -5),
                                settling_time=settling_time,
                                samples=5,
                                sub_directory=subdirectory
                                )
    #Tests.beam_power_dependence_rf_power_sweep(test_system_object=test_sys,
    #                            frequency=rf_frequency,
    #                            output_power_levels=range(-4, -25, -5),
    #                            settling_time=settling_time,
    #                            samples=5,
    #                            sub_directory=subdirectory
    #                            )

    # Tests.beam_position_equidistant_grid_raster_scan_test(test_system_object=test_sys,
    #                                                      rf_frequency=rf_frequency,
    #                                                      output_power_level=-6,
    #                                                      x_points=3,
    #                                                      y_points=3,
    #                                                      settling_time=settling_time,
    #                                                      samples=100,
    #                                                      sub_directory=subdirectory
    #                                                      )
    print '\nData stored in ', subdirectory
    return subdirectory


dls_rf_frequency = 499.655  # MHz.
data_store_location = sys.argv[1]
sys1 = Test_system_common.TestSystem(bpm_epics_id='TS-DI-EBPM-05',
                                     rf_hw='Rigol3030DSG', bpm_hw='Libera_Brilliance', atten_hw='MC_RC4DAT6G95')
subdirectory1 = tests_for_single_bpm(test_sys=sys1, data_location=data_store_location,
                                     rf_frequency=dls_rf_frequency, settling_time=0.1)
Latex_Report.assemble_report(subdirectory=subdirectory1)
print 'Data stored in ', subdirectory1

