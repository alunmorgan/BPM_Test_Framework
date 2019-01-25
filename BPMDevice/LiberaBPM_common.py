from pkg_resources import require
require("cothread==2.15")
from cothread.catools import caget, caput, connect
from subprocess import Popen, PIPE
import numpy as np
from BPM_helper_functions import Accumulator


def read_epics_pv(epics_id, pv):
    """Private method to read an Epics process variable.

    Wraps up caget call, makes it easy for multiple reads to be programmed
    and a timeout added if required. CA types are mapped to standard python types where possible.

    Args:
        epics_id (Str): The EPICS name of the device.
        pv (str): Name of the Epics process variable to read.
    Returns:
        pv_val: Value of requested process variable.
    """
    return caget(':'.join((epics_id, pv)))  # Get PV data


def write_epics_pv(epics_id, pv, val):
    """Private method to write to an Epics process variable.

    Wraps up caget call, makes it easy for multiple reads to be programmed
    and a timeout added if required.

    Args:
        epics_id (Str): The EPICS name of the device.
        pv (str): Name of the Epics process variable to read.
        val (str, int, float): Value to write to the process variable.
    Returns:
        variant: Value of requested process variable.
    """
    return caput(':'.join((epics_id, pv)), val)  # Write PV data


def get_mac_address(epics_id):
    """
    Args:
        epics_id (Str): The EPICS name of the device.
    Returns:
         str: mac address of the device.
    """
    pv = "SA:X"  # Any PV hosts on the device could be used here
    node = connect(':'.join((epics_id, pv)), cainfo=True).host.split(":")[0]  # Get the IP address of the host
    host_info = Popen(["arp", "-n", node], stdout=PIPE).communicate()[0]  # Uses arp to get more info about the host
    host_info = host_info.split("\n")[1]  # Splits the data about the host
    index = host_info.find(":")  # Gets the first ":", used in the MAC address
    host_info = host_info[index - 2:index + 15]  # Gets the devices MAC address
    return host_info


def get_attenuation(epics_id):
    """Override method, gets the internal attenuation setting.

    Args:
        epics_id (Str): The EPICS name of the device.
    Returns:
        float: Attenuation (dB)
        """
    return read_epics_pv(epics_id, "CF:ATTEN_S")


def set_attenuation(epics_id, attn):
    """Override method, sets the internal attenuation setting.


    Args:
        epics_id (Str): The EPICS name of the device.
        attn (float): Attenuation (dB)
        """
    write_epics_pv(epics_id, "CF:ATTEN_S", attn)


def get_x_position(epics_id):
    """Override method, gets the calculated X position of the beam.

    Args:
        epics_id (Str): The EPICS name of the device.
    Returns:
        float: X position in mm
    """
    return read_epics_pv(epics_id, "SA:X")  # Reads the requested PV


def get_y_position(epics_id):
    """Override method, gets the calculated Y position of the beam.

    Args:
        epics_id (Str): The EPICS name of the device.
    Returns:
        float: Y position in mm
    """
    return read_epics_pv(epics_id, "SA:Y")  # Reads the requested PV


def get_x_sa_data(epics_id, num_vals):
    """Gets the calculated X position SA data.

    Args:
        epics_id (Str): The EPICS name of the device.
        num_vals (int): The number of samples to capture
    Returns:
        timestamps (list): floats
        data (list): floats
    """
    sa_x_accum = Accumulator(':'.join((epics_id, 'SA:X')), num_vals)
    times, data = sa_x_accum.wait()
    times_rel = [x - times[0] for x in times]
    return times_rel, data


def get_y_sa_data(epics_id, num_vals):
    """Gets the calculated X position SA data.

    Args:
        epics_id (Str): The EPICS name of the device.
        num_vals (int): The number of samples to capture
    Returns:
        timestamps (list): floats
        data (list): floats
    """
    sa_y_accum = Accumulator(':'.join((epics_id, 'SA:Y')), num_vals)
    times, data = sa_y_accum.wait()
    times_rel = [x - times[0] for x in times]
    return times_rel, data


def get_sa_data(epics_id, num_vals):
    """Gets the ABCD SA data.

    Args:
        epics_id (Str): The EPICS name of the device.
        num_vals (int): The number of samples to capture
    Returns:
        timestamps (list): floats
        data (list): floats
    """
    sa_a_accum = Accumulator(''.join((epics_id, 'SA:A')), num_vals)
    sa_a_times, sa_a_data = sa_a_accum.wait()
    sa_b_accum = Accumulator(''.join((epics_id, 'SA:B')), num_vals)
    sa_b_times, sa_b_data = sa_b_accum.wait()
    sa_c_accum = Accumulator(''.join((epics_id, 'SA:C')), num_vals)
    sa_c_times, sa_c_data = sa_c_accum.wait()
    sa_d_accum = Accumulator(''.join((epics_id, 'SA:D')), num_vals)
    sa_d_times, sa_d_data = sa_d_accum.wait()

    return sa_a_times, sa_a_data, sa_b_times, sa_b_data, sa_c_times, sa_c_data, sa_d_times, sa_d_data


def get_tt_data(epics_id):
    """ Gets the calculated ABCD TT data.

    Args:
        epics_id (Str): The EPICS name of the device.
   Returns:
        times (list): floats
        data (list): floats
    """
    write_epics_pv(epics_id, 'TT:CAPLEN_S', 131072)
    write_epics_pv(epics_id, 'TT:DELAY_S', 0)
    write_epics_pv(epics_id, 'TT:ARM', 1)
    data1 = read_epics_pv(epics_id, "TT:WFA")
    data2 = read_epics_pv(epics_id, "TT:WFA")
    data3 = read_epics_pv(epics_id, "TT:WFA")
    data4 = read_epics_pv(epics_id, "TT:WFA")

    times = np.arange(len(data1)) * 936. / 500e6  # Each tick is one turn
    return times, data1, data2, data3, data4


def get_adc_data(epics_id, num_bits):
    """ Gets the ABCD ADC data.

    Args:
        epics_id (Str): The EPICS name of the device.
        num_bits (int): The number of bits the ADC has.
    Returns:
        timestamps (list): floats
        adc1_data (list): floats
        adc2_data (list): floats
        adc3_data (list): floats
        adc4_data (list): floats
    """
    # num_bits = 16  # The libera return the values centred around the centre bit of a 16 bit number
    adc1_data = read_epics_pv(epics_id, 'FT:RAW1')
    adc2_data = read_epics_pv(epics_id, 'FT:RAW2')
    adc3_data = read_epics_pv(epics_id, 'FT:RAW3')
    adc4_data = read_epics_pv(epics_id, 'FT:RAW4')
    # The data is centred on the middle bits. Shift it so all values are positive.
    half_range = np.power(2, num_bits) / 2
    adc1_out = [int(x + half_range) for x in adc1_data]
    adc2_out = [int(x + half_range) for x in adc2_data]
    adc3_out = [int(x + half_range) for x in adc3_data]
    adc4_out = [int(x + half_range) for x in adc4_data]
    times = np.arange(len(adc1_out)) * 1 / 117E6  # Data rate is 117MHz
    if not adc1_out or not adc2_out or not adc3_out or not adc4_out:
        raise ValueError('Not all ADC data returned.')
    return list(times), [adc1_out, adc2_out, adc3_out, adc4_out]


def get_ft_data(epics_id):
    """ Gets the ABCD first turn data.

    Args:
        epics_id (Str): The EPICS name of the device.
   Returns:
        timestamps (list): floats
        data (list): floats
    """
    write_epics_pv(epics_id, 'FT:ENABLE_S', 1)
    fta_data = read_epics_pv(epics_id, ':WFA')
    ftb_data = read_epics_pv(epics_id, ':WFB')
    ftc_data = read_epics_pv(epics_id, ':WFC')
    ftd_data = read_epics_pv(epics_id, ':WFD')
    write_epics_pv(epics_id, 'FT:ENABLE_S', 0)
    times = np.arange(len(fta_data)) * 1 / 30E6  # Data rate is 30MHz
    return times, fta_data, ftb_data, ftc_data, ftd_data


def get_beam_current(epics_id):
    """Override method, gets the beam current read by the BPMs.

    Args:
        epics_id (Str): The EPICS name of the device.
    Returns:
        float: Current in mA
    """
    return read_epics_pv(epics_id, "SA:CURRENT")  # Reads the requested PV


def get_input_power(epics_id):
    """Override method, gets the input power of the signals input to the device

    Args:
        epics_id (Str): The EPICS name of the device.
    Returns:
        float: Input power in dBm
    """
    return read_epics_pv(epics_id, "SA:POWER")  # Reads the requested PV


def get_raw_bpm_buttons(epics_id):
    """Override method, gets the raw signal from each BPM.

    Args:
        epics_id (Str): The EPICS name of the device.
    Returns:
        float: Raw signal from BPM A
        float: Raw signal from BPM B
        float: Raw signal from BPM C
        float: Raw signal from BPM D
    """
    return (read_epics_pv(epics_id, "SA:A"),
            read_epics_pv(epics_id, "SA:B"),
            read_epics_pv(epics_id, "SA:C"),
            read_epics_pv(epics_id, "SA:D"))  # Reads the requested PVs


def get_normalised_bpm_buttons(epics_id):
    """Override method, gets the normalised signal from each BPM.

    Args:
        epics_id (Str): The EPICS name of the device.
    Returns:
        float: Normalised signal from BPM A
        float: Normalised signal from BPM B
        float: Normalised signal from BPM C
        float: Normalised signal from BPM D
    """
    return (read_epics_pv(epics_id, "SA:AN"),
            read_epics_pv(epics_id, "SA:BN"),
            read_epics_pv(epics_id, "SA:CN"),
            read_epics_pv(epics_id, "SA:DN"))  # Reads the requested PVs


def get_adc_sum(epics_id):
    """Override method, gets the sum of all of the buttons ADCs

    A+B+C+D

    Args:
        epics_id (Str): The EPICS name of the device.
    Returns:
        int: ADC sum in counts
    """
    a, b, c, d = get_raw_bpm_buttons(epics_id)  # Reads the requested PVs
    adc_sum = a + b + c + d  # Sums the values of the PVs
    return adc_sum
