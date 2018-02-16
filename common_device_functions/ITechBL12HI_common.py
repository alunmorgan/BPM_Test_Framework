
import telnetlib
import re


def telnet_query(ipaddress, port, timeout, orig_message):
    """Private method that will send a message over telnet to the ITechBL12HI and return the reply.
        This needs to open and close a connection in order to isolate the replies. If one connection is opened on
        this hardware the responses do not block so several responses can arrive before the first read.
        So the wrong data is read.

    Args:
        message (str): SCPI message to be sent to the ITechBL12HI

    Returns:
        str: Reply message from the ITechBL12HI
    """
    # Checks that the telnet message is a string
    if type(orig_message) != str:
        raise TypeError
    tn = telnetlib.Telnet(ipaddress, port, timeout)  # Connects to the IP via telnet
    tn.read_until("\n", timeout).rstrip('\n')
    tn.read_until("\n", timeout).rstrip('\n')
    tn.write("scpi>\r\n")  # putting the device into scpi mode.
    tn.write(orig_message + "\r\n")  # Writes a telnet message with termination characters
    r_str = tn.read_until("\n", timeout).rstrip('\n')  # Telnet reply, with termination chars removed
    message_pattern = re.compile('(?:scpi>)*\S*\s+(.*)')
    message = re.match(message_pattern, r_str)
    # Status line. Needs to be read to make the following read be at the correct place
    check = tn.read_until("\n", timeout).rstrip('\n')  # Status line
    tn.close()  # Closes the telnet connection
    if 'OK' not in check:
        print "Original message = ", orig_message
        print 'Bad status  STATUS = ', check
        print 'Returned command = ', r_str
        if message is not None:
            print 'Return = ', message.group(1)
        raise ValueError("Bad status on communication with ITechBL12HI")
    return message.group(1), check


def get_device_identity(ipaddress, port, timeout):
    """Override method that will return the device ID.

    Uses the SCPI command "*IDN?" to get the device ID.

    Args:

    Returns:
        str: The DeviceID of the SigGen.
    """
    device_id, check = telnet_query(ipaddress, port, timeout, "*IDN?\r\n")  # gets the device information
    if "IT CLKGEN" not in device_id:  # checks it's the right device
        print "ID= ", device_id
        raise ValueError("Wrong hardware device connected")
    return device_id


def turn_rf_on(ipaddress, port, timeout, Output_Power):
    """Override method that will turn on the RF device output.

    Set the level to the requested power. This hardware does not have the ability to turn the RF source on and off.

    Args:

    Returns:
        bool: Returns True if the output is enabled, False if it is not.
    """
    # turns on the output
    ret, check = telnet_query(ipaddress, port, timeout, "POW:RF " + str(Output_Power))
    if "OK" not in check:
        raise ValueError("Turning RF on unsuccessful. Power setting in unknown state.")
    # Turns on the modulation state output
    ret, check = telnet_query(ipaddress, port, timeout, "GATE:FILL 100")
    if "OK" not in check:
        raise ValueError("Turning RF on unsuccessful. Gate setting in unknown state.")


def turn_rf_off(ipaddress, port, timeout):
    """Override method that will turn off the RF device output.

    This device does not have the ability to turn off the RF source.
    Instead it is turned down to the lowest level.

    Args:

    Returns:
        bool: Returns True if the output is enabled, False if it is not.
    """
    # turns off the output
    ret, check = telnet_query(ipaddress, port, timeout, "POW:RF -50")
    if "OK" not in check:
        raise ValueError("Turning RF off unsuccessful. Power setting in unknown state.")
    # Turns off the modulation state output
    ret, check = telnet_query(ipaddress, port, timeout, "GATE:FILL 0")
    if "OK" not in check:
        raise ValueError("Turning RF off unsuccessful. Gate setting in unknown state.")

