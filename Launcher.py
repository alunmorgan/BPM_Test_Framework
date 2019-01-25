import sys
import os
import time
import Test_system_common
import Latex_Report
import Tests
import json
from pkg_resources import require
require("numpy == 1.11.1")
# require("matplotlib")
require("scipy == 0.19.1")
import numpy as np


SYS = Test_system_common.TestSystem(rf_hw='Rigol3030DSG', bpm_hw='Libera_Electron', atten_hw='MC_RC4DAT6G95')

root_path = '/'.join((sys.argv[1], SYS.BPM.mac_address.replace(':', '-'), time.strftime("%d-%m-%Y_T_%H-%M")))
if not os.path.exists(root_path):
    os.makedirs(root_path)

# report = Latex_Report.Tex_Report('/'.join((root_path, "BPMTestReport")), BPM.mac_address)

dls_RF_frequency = 499.655  # MHz. For the ITECH hardware you can only set RF in steps of 5kHz.
dls_bunch = 1. / (dls_RF_frequency / 936.)  # us
trigger_frequency = dls_RF_frequency / 100.  # used as Hz
subdirectory = ''.join((root_path, '/'))
settling_time = 0.1

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

Tests.adc_test(test_system_object=SYS,
               frequency=dls_RF_frequency,
               output_power_level=-4,
               settling_time=settling_time,
               sub_directory=subdirectory
               )

Tests.adc_int_atten_sweep_test(test_system_object=SYS,
                               frequency=dls_RF_frequency,
                               output_power_level=-4,
                               settling_time=settling_time,
                               sub_directory=subdirectory)

Tests.beam_power_dependence(test_system_object=SYS,
                            frequency=dls_RF_frequency,
                            output_power_levels=range(-4, -30, -5),
                            settling_time=settling_time,
                            samples=100,
                            sub_directory=subdirectory
                            )


Tests.beam_position_equidistant_grid_raster_scan_test(test_system_object=SYS,
                                                      rf_frequency=dls_RF_frequency,
                                                      output_power_level=-10,
                                                      x_points=9,
                                                      y_points=9,
                                                      settling_time=settling_time,
                                                      sub_directory=subdirectory
                                                      )

print 'Data stored in ', subdirectory
# Latex_Report.assemble_report(subdirectory=subdirectory)
# print 'Report written to ', subdirectory
