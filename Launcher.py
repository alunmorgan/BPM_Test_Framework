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


RF = RFSignalGenerators.Rigol3030DSG_RFSigGen(
    ipaddress="172.23.252.51",
    port=5555,
    timeout=1,
    limit=-40)

GS = Gate_Source.Rigol3030DSG_GateSource(
    ipaddress="172.23.252.51",
    port=5555,
    timeout=1)

Trigger = Trigger_Source.agilent33220a_wfmgen(
    ipaddress="172.23.252.204",
    port=5024,
    timeout=1)

ProgAtten = ProgrammableAttenuator.MC_RC4DAT6G95_Prog_Atten(
    ipaddress="172.23.244.105",
    port=23,
    timeout=1)

BPM = BPMDevice.Electron_BPMDevice(
    dev_ID="TS-DI-EBPM-05:")

root_path = '/'.join((sys.argv[1], BPM.macaddress.replace(':', '-'), time.strftime("%d-%m-%Y_T_%H-%M")))
print root_path
if not os.path.exists(root_path):
    os.makedirs(root_path)

report = Latex_Report.Tex_Report('/'.join((root_path, "BPMTestReport")), BPM.macaddress)

dls_RF_frequency = 499.6817682  # MHz
dls_bunch = 1.87319
trigger_frequency = dls_RF_frequency / 100.  # used as Hz
subdirectory = ''.join((root_path, '/'))
settling_time = 0

# Initial setup of the triggers
Trigger.set_up_trigger_pulse(freq=trigger_frequency)

# Tests.Beam_position_equidistant_grid_raster_scan_test(
#     RFObject=RF,
#     BPMObject=BPM,
#     ProgAttenObject=ProgAtten,
#     rf_frequency=dls_RF_frequency,
#     rf_power=-40,
#     nominal_attenuation=10,
#     x_points=3,
#     y_points=3,
#     settling_time=settling_time,
#     ReportObject=report,
#     sub_directory=subdirectory)
#
# Tests.Beam_position_attenuation_permutation_test(
#     RFObject=RF,
#     BPMObject=BPM,
#     ProgAttenObject=ProgAtten,
#     rf_frequency=dls_RF_frequency,
#     rf_power=-40,
#     attenuator_max=50,
#     attenuator_min=10,
#     attenuator_steps=2,
#     settling_time=settling_time,
#     ReportObject=report,
#     sub_directory=subdirectory)
#
# ProgAtten.set_global_attenuation(0)
#
# Tests.Beam_Power_Dependence(
#     RFObject=RF,
#     BPMObject=BPM,
#     frequency=dls_RF_frequency,
#     start_power=-100,
#     end_power=-40,
#     samples=10,
#     settling_time=settling_time,
#     ReportObject=report,
#     sub_directory=subdirectory)
#
# Tests.Fixed_voltage_amplitude_fill_pattern_test(
#     RFObject=RF,
#     BPMObject=BPM,
#     GateSourceObject=GS,
#     frequency=dls_RF_frequency,
#     power=-40,
#     samples=10,
#     pulse_period=dls_bunch,
#     settling_time=settling_time,
#     ReportObject=report,
#     sub_directory=subdirectory)
#
# Tests.Scaled_voltage_amplitude_fill_pattern_test(
#     RFObject=RF,
#     BPMObject=BPM,
#     GateSourceObject=GS,
#     frequency=dls_RF_frequency,
#     desired_power=-70,
#     samples=10,
#     pulse_period=dls_bunch,
#     settling_time=settling_time,
#     ReportObject=report,
#     sub_directory=subdirectory)

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

