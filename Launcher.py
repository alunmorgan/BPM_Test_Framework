import sys
import os
import time
import RFSignalGenerators
import BPMDevice
import Gate_Source
import Trigger_Source
import ProgrammableAttenuator
import Latex_Report
import Tests
import numpy as np

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
    ipaddress="172.23.252.102",
    port=23,
    timeout=10,
    limit=-40)
# time.sleep(10)
print 'Initialising Gate'
GS = Gate_Source.ITechBL12HI_GateSource(
    ipaddress="172.23.252.102",
    port=23,
    timeout=10)
# time.sleep(10)
print 'Initialising Trigger'
Trigger = Trigger_Source.ITechBL12HI_trigsrc(
    ipaddress="172.23.252.102",
    port=23,
    timeout=10)
# time.sleep(10)
print 'Initialising programmable attenuator'
ProgAtten = ProgrammableAttenuator.MC_RC4DAT6G95_Prog_Atten(
    ipaddress="172.23.244.105",
    port=23,
    timeout=2)
# time.sleep(10)
print 'Initialising BPM'
BPM = BPMDevice.Electron_BPMDevice(
    dev_ID="TS-DI-EBPM-05:")
# time.sleep(10)

root_path = '/'.join((sys.argv[1], BPM.macaddress.replace(':', '-'), time.strftime("%d-%m-%Y_T_%H-%M")))
print root_path
if not os.path.exists(root_path):
    os.makedirs(root_path)

report = Latex_Report.Tex_Report('/'.join((root_path, "BPMTestReport")), BPM.macaddress)

dls_RF_frequency = 499.654  # MHz. For the ITECH hardware you can only set RF in steps of 5kHz.
dls_bunch = 1. / (dls_RF_frequency / 936.)  # us
trigger_frequency = dls_RF_frequency / 100.  # used as Hz
subdirectory = ''.join((root_path, '/'))
settling_time = 0

print 'Setting up triggers'
# Initial setup of the triggers
Trigger.set_up_trigger_pulse(freq=trigger_frequency)

Tests.beam_position_equidistant_grid_raster_scan_test(
    rf_object=RF,
    bpm_object=BPM,
    prog_atten_object=ProgAtten,
    rf_frequency=dls_RF_frequency,
    rf_power=-40,
    nominal_attenuation=10,
    x_points=3,
    y_points=3,
    settling_time=settling_time,
    report_object=report,
    sub_directory=subdirectory)

Tests.beam_position_attenuation_permutation_test(
    rf_object=RF,
    bpm_object=BPM,
    prog_atten_object=ProgAtten,
    rf_frequency=dls_RF_frequency,
    rf_power=-40,
    attenuator_max=50,
    attenuator_min=10,
    attenuator_steps=2,
    settling_time=settling_time,
    report_object=report,
    sub_directory=subdirectory)

Tests.beam_power_dependence(
    rf_object=RF,
    bpm_object=BPM,
    prog_atten_object=ProgAtten,
    frequency=dls_RF_frequency,
    power_levels=np.arange(-40, -100, -10),
    settling_time=settling_time,
    report_object=report,
    sub_directory=subdirectory)

Tests.fixed_voltage_amplitude_fill_pattern_test(
    rf_object=RF,
    bpm_object=BPM,
    prog_atten_object=ProgAtten,
    gate_source_object=GS,
    frequency=dls_RF_frequency,
    max_power=-40,
    duty_cycles=np.range(1, 0, -0.1),
    pulse_period=dls_bunch,
    settling_time=settling_time,
    report_object=report,
    sub_directory=subdirectory)

Tests.scaled_voltage_amplitude_fill_pattern_test(
    rf_object=RF,
    bpm_object=BPM,
    prog_atten_object=ProgAtten,
    gate_source_object=GS,
    frequency=dls_RF_frequency,
    max_power=-40,
    duty_cycles=np.arange(1, 0, -0.1),
    pulse_period=dls_bunch,
    settling_time=settling_time,
    report_object=report,
    sub_directory=subdirectory)

ProgAtten.set_global_attenuation(0)

Tests.adc_test(
    rf_object=RF,
    bpm_object=BPM,
    frequency=dls_RF_frequency,
    power_levels=(-70.,),
    samples=10,
    settling_time=settling_time,
    report_object=report,
    sub_directory=subdirectory)

report.create_report()

