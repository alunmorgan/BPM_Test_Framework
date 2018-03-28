from pkg_resources import require
require("numpy")
require("cothread")
require("matplotlib")
require("scipy")
import sys
import os
import time
import Test_system_common
import RFSignalGenerators
import BPMDevice
import Gate_Source
import Trigger_Source
import ProgrammableAttenuator
#import Latex_Report
import Tests
import numpy as np
from scipy.io import savemat

# RF = RFSignalGenerators.Rigol3030DSG_RFSigGen(
#     ipaddress="172.23.252.51",
#     port=5555,
#     timeout=1,
#     limit=-40)
#
# GS = Gate_Source.Rigol3030DSG_GateSource(
#     ipaddress="172.23.252.51",
#     port=5555,
#     timeout=1)
#
# Trigger = Trigger_Source.agilent33220a_wfmgen(
#     ipaddress="172.23.252.204",
#     port=5024,
#     timeout=1)
print 'Initialising RF source'
RF = RFSignalGenerators.ITechBL12HI_RFSigGen(
    ipaddress="172.23.234.129",#"172.23.252.102",  #172.223.206.20
    port=23,
    timeout=20,
    limit=10)
# time.sleep(10)
print 'Initialising Gate'
GS = Gate_Source.ITechBL12HI_GateSource(RF.tn, RF.timeout)
# time.sleep(10)
print 'Initialising Trigger'
Trigger = Trigger_Source.ITechBL12HI_trigsrc(RF.tn, RF.timeout)
# time.sleep(10)
print 'Initialising programmable attenuator'
ProgAtten = ProgrammableAttenuator.MC_RC4DAT6G95_Prog_Atten(
    ipaddress="172.23.234.130",  #"172.23.244.105",  # 172.23.206.21
    port=23,
    timeout=10)
# time.sleep(10)
if sys.argv[3] == 'E':
    print 'Initialising Electron BPM'
    BPM = BPMDevice.ElectronBPMDevice(dev_id=''.join((sys.argv[2], ':')))
elif sys.argv[3] == 'B':
    print 'Initialising Brilliance BPM'
    BPM = BPMDevice.BrillianceBPMDevice(dev_id=''.join((sys.argv[2], ':')))
else:
    raise ValueError('You need to select E for Electron or B for Brilliance.')

# Pulling the IDs here as some hardware is not as well behaved when using telnet as one would like.
# This reduces the number of telnet calls in individual tests.
SYS = Test_system_common.TestSystem(rf_hw=RF, gate_hw=GS, trigger_hw=Trigger, bpm_hw=BPM)

root_path = '/'.join((sys.argv[1], BPM.mac_address.replace(':', '-'), time.strftime("%d-%m-%Y_T_%H-%M")))
if not os.path.exists(root_path):
    os.makedirs(root_path)

#report = Latex_Report.Tex_Report('/'.join((root_path, "BPMTestReport")), BPM.mac_address)

dls_RF_frequency = 499.655  # MHz. For the ITECH hardware you can only set RF in steps of 5kHz.
dls_bunch = 1. / (dls_RF_frequency / 936.)  # us
trigger_frequency = dls_RF_frequency / 100.  # used as Hz
subdirectory = ''.join((root_path, '/'))
settling_time = 0.2
#spec = BPM.get_performance_spec()

savemat(subdirectory + "initial_BPM_state" + ".mat",
        {'epics_id': BPM.epics_id,
         'mac_address': BPM.mac_address,
         'first_turn': BPM.ft,
         'agc': BPM.agc,
         'delta': BPM.delta,
         'switches': BPM.switches,
         'switch_val': BPM.switch_val,
         'attenuation': BPM.attn,
         'dsc': BPM.dsc,
         'kx': BPM.kx,
         'ky': BPM.ky})


ProgAtten.set_global_attenuation(0)

print 'Setting up triggers'
# Initial setup of the triggers
Trigger.set_up_trigger_pulse(freq=trigger_frequency)

Tests.adc_test(
               test_system_object=SYS,
               rf_object=RF,
               bpm_object=BPM,
               prog_atten_object=ProgAtten,
               frequency=dls_RF_frequency,
               power_level=-40,
               settling_time=10,
               sub_directory=subdirectory)

Tests.adc_int_atten_sweep_test(
               test_system_object=SYS,
               rf_object=RF,
               bpm_object=BPM,
               prog_atten_object=ProgAtten,
               frequency=dls_RF_frequency,
               power_level=-10,
               external_attenuation=60,
               attenuation_levels=np.arange(0, 62, 2),
               settling_time=.2,
               sub_directory=subdirectory)

Tests.beam_power_dependence(
    test_system_object=SYS,
    rf_object=RF,
    bpm_object=BPM,
    prog_atten_object=ProgAtten,
    frequency=dls_RF_frequency,
    power_levels=np.arange(-6, -85, -5),
    settling_time=0.2,
    samples=10,
    sub_directory=subdirectory)

Tests.fixed_voltage_amplitude_fill_pattern_test(
    test_system_object=SYS,
    rf_object=RF,
    bpm_object=BPM,
    prog_atten_object=ProgAtten,
    gate_source_object=GS,
    frequency=dls_RF_frequency,
    max_power=-6,
    duty_cycles=np.arange(1, 0, -0.1),
    pulse_period=dls_bunch,
    settling_time=settling_time,
    samples=10,
    sub_directory=subdirectory)

Tests.scaled_voltage_amplitude_fill_pattern_test(
    test_system_object=SYS,
    rf_object=RF,
    bpm_object=BPM,
    prog_atten_object=ProgAtten,
    gate_source_object=GS,
    frequency=dls_RF_frequency,
    max_power=-6,
    duty_cycles=np.arange(1, 0, -0.1),
    pulse_period=dls_bunch,
    settling_time=settling_time,
    samples=10,
    sub_directory=subdirectory)

# Tests.beam_position_equidistant_grid_raster_scan_test(
#     test_system_object=SYS,
#     rf_object=RF,
#     bpm_object=BPM,
#     prog_atten_object=ProgAtten,
#     rf_frequency=dls_RF_frequency,
#     power_level=-6,
#     nominal_attenuation=10,
#     x_points=5,
#     y_points=5,
#     settling_time=settling_time,
#     report_object=report,
#     sub_directory=subdirectory)


# report.create_report()
