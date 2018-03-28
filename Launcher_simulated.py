import sys
import os
import time
import RFSignalGenerators
import BPMDevice
import Gate_Source
import ProgrammableAttenuator
import Latex_Report
import Tests
import numpy as np


RF = RFSignalGenerators.Simulated_RFSigGen(limit=-40, noise_mag=1)
GS = Gate_Source.Simulated_GateSource()
ProgAtten = ProgrammableAttenuator.Simulated_Prog_Atten()
BPM = BPMDevice.SimulatedBPMDevice(rf_sim=RF, gatesim=GS, progatten=ProgAtten, noise_mag=1)

root_path = '/'.join((sys.argv[1], BPM.macaddress.replace(':', '-'), time.strftime("%d-%m-%Y_T_%H-%M")))
print root_path
if not os.path.exists(root_path):
    os.makedirs(root_path)

report = Latex_Report.Tex_Report('/'.join((root_path, "BPMTestReport")), BPM.macaddress)

dls_RF_frequency = 499.6817682
dls_bunch = 1. / (dls_RF_frequency / 936.)  # us
subdirectory = ''.join((root_path, '/'))
settling_time = 0

ProgAtten.set_global_attenuation(0)

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
    duty_cycles=np.arange(1, 0, -0.1),
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

Tests.noise_test(rf_object=RF,
                 bpm_object=BPM,
                 frequency=dls_RF_frequency,
                 start_power=-100,
                 end_power=-40,
                 samples=10,
                 settling_time=settling_time,
                 report_object=report,
                 sub_directory=subdirectory)

Tests.adc_test(rf_object=RF,
               bpm_object=BPM,
               prog_atten_object=ProgAtten,
               frequency=1,
               samples=1000,
               power_levels=(-40., -50.),
               settling_time=1,
               report_object=report,
               sub_directory=subdirectory)

report.create_report()

