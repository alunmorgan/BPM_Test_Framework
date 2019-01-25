import sys
import os
import time
from pkg_resources import require
require('numpy == 1.11.1')
require('scipy == 0.19.1')
require("matplotlib")
import numpy as np
import Test_system_common
import Latex_Report
import Tests
import json
# from scipy.io import savemat

SYS = Test_system_common.TestSystem(rf_hw='Simulated', bpm_hw='Simulated', atten_hw='Simulated')

root_path = '/'.join((sys.argv[1], SYS.BPM.mac_address.replace(':', '-'), time.strftime("%d-%m-%Y_T_%H-%M")))
print root_path
if not os.path.exists(root_path):
    os.makedirs(root_path)

# report = Latex_Report.Tex_Report('/'.join((root_path, "BPMTestReport")), SYS.BPM.macaddress)

dls_RF_frequency = 499.6817682
dls_bunch = 1. / (dls_RF_frequency / 936.)  # us
subdirectory = ''.join((root_path, '/'))
settling_time = 0


data_out = {'epics_id': SYS.BPM.epics_id,
            'mac_address': SYS.BPM.mac_address,
            'first_turn': SYS.BPM.ft,
            'agc': SYS.BPM.agc,
            'delta': SYS.BPM.delta,
            'switches': SYS.BPM.switches,
            'switch_val': SYS.BPM.switch_val,
            'attenuation': SYS.BPM.attn,
            'dsc': SYS.BPM.dsc,
            'kx': SYS.BPM.kx,
            'ky': SYS.BPM.ky}

with open(subdirectory + "initial_BPM_state.json", 'w') as write_file:
    json.dump(data_out, write_file)

Tests.beam_position_equidistant_grid_raster_scan_test(test_system_object=SYS,
                                                      rf_frequency=dls_RF_frequency,
                                                      power_level=-40,
                                                      nominal_attenuation=10,
                                                      x_points=3,
                                                      y_points=3,
                                                      settling_time=settling_time,
                                                      sub_directory=subdirectory
                                                      )

Tests.beam_power_dependence(test_system_object=SYS,
                            frequency=dls_RF_frequency,
                            power_levels=np.arange(-40, -100, -10),
                            settling_time=settling_time,
                            sub_directory=subdirectory
                            )

# Tests.fixed_voltage_amplitude_fill_pattern_test(test_system_object=SYS,
#                                                 frequency=dls_RF_frequency,
#                                                 max_power=-40,
#                                                 duty_cycles=np.arange(1, 0, -0.1),
#                                                 pulse_period=dls_bunch,
#                                                 settling_time=settling_time,
#                                                 sub_directory=subdirectory
#                                                 )
#
# Tests.bunch_train_length_dependency_test(test_system_object=SYS,
#                                          frequency=dls_RF_frequency,
#                                          max_power=-40,
#                                          duty_cycles=np.arange(1, 0, -0.1),
#                                          pulse_period=dls_bunch,
#                                          settling_time=settling_time,
#                                          sub_directory=subdirectory
#                                          )

Tests.noise_test(test_system_object=SYS,
                 frequency=dls_RF_frequency,
                 power_levels=np.arange(-20, -50, -5),
                 samples=10,
                 settling_time=settling_time,
                 sub_directory=subdirectory
                 )

Tests.adc_test(test_system_object=SYS,
               frequency=1,
               power_level=-40,
               settling_time=10,
               sub_directory=subdirectory
               )

Tests.adc_int_atten_sweep_test(test_system_object=SYS,
                               frequency=dls_RF_frequency,
                               power_level=-20,
                               external_attenuation=60,
                               attenuation_levels=np.arange(0, 62, 2),
                               settling_time=settling_time,
                               sub_directory=subdirectory)

Latex_Report.assemble_report(subdirectory=subdirectory)
# report.create_report()

