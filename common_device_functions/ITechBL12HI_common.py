
import telnetlib
import re


def telnet_setup(ipaddress, port, timeout):
    tn = telnetlib.Telnet(ipaddress, port, timeout)  # Connects to the IP via telnet
    tn.read_until("\n", timeout).rstrip('\n')
    tn.read_until("\n", timeout).rstrip('\n')
    tn.write("scpi>\r\n")  # putting the device into scpi mode.
    return tn


def telnet_query(tn, timeout, orig_message):
    """Private method that will send a message over telnet to the ITechBL12HI and return the reply.
        This needs to open and close a connection in order to isolate the replies. If one connection is opened on
        this hardware the responses do not block so several responses can arrive before the first read.
        So the wrong data is read.

    Args:
        orig_message (str): SCPI message to be sent to the ITechBL12HI

    Returns:
        str: Reply message from the ITechBL12HI
    """
    # Expected message pattern
    message_pattern = re.compile('(?:scpi>)*\S*\s+(.*)')

    # Checks that the telnet message is a string
    if type(orig_message) != str:
        raise TypeError
    tn.write(orig_message + "\r\n")  # Writes a telnet message with termination characters
    r_str = tn.read_until("\n", timeout).rstrip('\n')  # Telnet reply, with termination chars removed
    check = tn.read_until("\n", timeout).rstrip('\n')  # Status line
    message = re.match(message_pattern, r_str)

    if 'OK' not in check:
        #Have another go
        print 'Retrying ', orig_message
        tn.write(orig_message + "\r\n")  # Writes a telnet message with termination characters
        r_str = tn.read_until("\n", timeout).rstrip('\n')  # Telnet reply, with termination chars removed
        check = tn.read_until("\n", timeout).rstrip('\n')  # Status line
        message = re.match(message_pattern, r_str)
        if 'OK' not in check:
            print "Original message = ", orig_message
            print 'Returned command = ', r_str
            print 'Bad status  STATUS = ', check
            if message is not None:
                print 'Return = ', message.group(1)
            raise ValueError(''.join(('Bad status on communication with ITechBL12HI: ', orig_message)))
    return message.group(1), check


def get_device_identity(tn, timeout):
    """Override method that will return the device ID.

    Uses the SCPI command "*IDN?" to get the device ID.

    Args:

    Returns:
        str: The DeviceID of the SigGen.
    """
    device_id, check = telnet_query(tn, timeout, "*IDN?\r\n")  # gets the device information
    if "IT CLKGEN" not in device_id:  # checks it's the right device
        print "ID= ", device_id
        raise ValueError("Wrong hardware device connected")
    return device_id


def turn_rf_on(tn, timeout, Output_Power):
    """Override method that will turn on the RF device output.

    Set the level to the requested power. This hardware does not have the ability to turn the RF source on and off.

    Args:

    Returns:
        bool: Returns True if the output is enabled, False if it is not.
    """
    # turns on the output
    ret, check = telnet_query(tn, timeout, "POW:RF " + str(Output_Power))
    if "OK" not in check:
        raise ValueError("Turning RF on unsuccessful. Power setting in unknown state.")
    # Turns on the modulation state output
    ret, check = telnet_query(tn, timeout, "GATE:FILL 100")
    if "OK" not in check:
        raise ValueError("Turning RF on unsuccessful. Gate setting in unknown state.")


def turn_rf_off(tn, timeout):
    """Override method that will turn off the RF device output.

    This device does not have the ability to turn off the RF source.
    Instead it is turned down to the lowest level.

    Args:

    Returns:
        bool: Returns True if the output is enabled, False if it is not.
    """
    # turns off the output
    ret, check = telnet_query(tn, timeout, "POW:RF -50")
    if "OK" not in check:
        raise ValueError("Turning RF off unsuccessful. Power setting in unknown state.")
    # Turns off the modulation state output
    ret, check = telnet_query(tn, timeout, "GATE:FILL 0")
    if "OK" not in check:
        raise ValueError("Turning RF off unsuccessful. Gate setting in unknown state.")

