from math import floor
import RFSignalGenerators
import BPMDevice
import Gate_Source
import Trigger_Source
import ProgrammableAttenuator

# rf_object(RFSignalGenerator
# Obj): Object
# to
# interface
# with the RF hardware.
# bpm_object(BPMDevice
# Obj): Object
# to
# interface
# with the BPM hardware.
# prog_atten_object(Prog_Atten
# Obj): Object
# to
# interface
# with programmable attenuator hardware
# gate_source_object: (GateSource Obj): Object
# used
# to
# interface
# with the gate source
# hardware.


class TestSystem:
    """This captures the behaviour of the system due to cabling losses"""

    def __init__(self, bpm_epics_id, rf_hw, bpm_hw, atten_hw, gate_hw=None, trigger_hw=None):
        self.rf_hw = rf_hw
        self.gate_hw = gate_hw
        self.bpm_hw = bpm_hw
        self.atten_hw = atten_hw
        self.trigger_hw = trigger_hw

        self.all_devices = {'RF_sources': {'Rigol3030DSG': {'ipaddress': "172.23.252.51", 'port': 5555,
                                                            'timeout': 1, 'limit': 10},
                                           'ITechBL12HI': {'ipaddress': "172.23.252.102", 'port': 23,
                                                           'timeout': 20, 'limit': 10},
                                           'Simulated': {'limit': 10, 'noise_mag': 1}},

                            'Modulation_sources': {'Rigol3030DSG': {'ipaddress': "172.23.252.51", 'port': 5555,
                                                                    'timeout': 1},
                                                   'ITechBL12HI': {'ipaddress': "172.23.252.102", 'port': 23,
                                                                   'timeout': 20},
                                                   'Simulated': {}},
                            'Trigger_sources': {'Agilent33220A': {'ipaddress': "172.23.252.204", 'port': 5024,
                                                                  'timeout': 1},
                                                'ITechBL12HI': {'ipaddress': "172.23.252.204", 'port': 5024,
                                                                'timeout': 1}},
                            'Programmable_attenuators': {'MC_RC4DAT6G95': {'ipaddress': "172.23.244.105", 'port': 23,
                                                                           'timeout': 10},
                                                         'Simulated': {}},
                            'BPM': {'Libera_Electron': {'damage_level': 0},
                                    'Libera_Brilliance': {'damage_level': 0},
                                    'Simulated': {'noise_mag': 1, 'damage_level': 2}}
                            }

        print 'Initialising RF source'
        if self.rf_hw == 'Rigol3030DSG':
            self.RF = RFSignalGenerators.Rigol3030DSG_RFSigGen(
                ipaddress=self.all_devices['RF_sources'][self.rf_hw]['ipaddress'],
                port=self.all_devices['RF_sources'][self.rf_hw]['port'],
                timeout=self.all_devices['RF_sources'][self.rf_hw]['timeout'],
                limit=self.all_devices['RF_sources'][self.rf_hw]['limit'])
            # The output from the RF source is fixed due to the requirements of the timing circuitry.
            self.rf_output = 5  # dBm
        elif rf_hw == 'ITechBL12HI':
            self.RF = RFSignalGenerators.ITechBL12HI_RFSigGen(
                ipaddress=self.all_devices['RF_sources'][self.rf_hw]['ipaddress'],
                port=self.all_devices['RF_sources'][self.rf_hw]['port'],
                timeout=self.all_devices['RF_sources'][self.rf_hw]['timeout'],
                limit=self.all_devices['RF_sources'][self.rf_hw]['limit'])
            # The output from the RF source is fixed due to the requirements of the timing circuitry.
            self.rf_output = 5  # dBm
        elif rf_hw == 'Simulated':
            self.RF = RFSignalGenerators.Simulated_RFSigGen(
                limit=self.all_devices['RF_sources'][self.rf_hw]['limit'],
                noise_mag=self.all_devices['RF_sources'][self.rf_hw]['noise_mag'])

        if self.gate_hw is not None:
            print 'Initialising Gate'
            if self.gate_hw == 'Rigol3030DSG':
                self.GS = Gate_Source.Rigol3030DSG_GateSource(self.RF.tn,
                                                              self.all_devices['Modulation_sources'][self.gate_hw][
                                                                  'timeout'])
            elif self.gate_hw == 'ITechBL12HI':
                self.GS = Gate_Source.ITechBL12HI_GateSource(self.RF.tn,
                                                             self.all_devices['Modulation_sources'][self.gate_hw][
                                                                 'timeout'])
            elif self.gate_hw == 'Simulated':
                self.GS = Gate_Source.Simulated_GateSource()
        elif self.gate_hw is None:
            self.GS = None

        if self.trigger_hw is not None:
            print 'Initialising Trigger'
            if self.trigger_hw == 'Agilent33220A':
                self.Trigger = Trigger_Source.Agilent33220A_trigsrc(self.RF.tn,
                                                                    self.all_devices['Trigger_sources'][
                                                                        self.trigger_hw]['timeout'])
            elif self.trigger_hw == 'ITechBL12HI':
                self.Trigger = Trigger_Source.ITechBL12HI_trigsrc(self.RF.tn,
                                                                  self.all_devices['Trigger_sources'][self.trigger_hw][
                                                                      'timeout'])
        elif self.trigger_hw is None:
            self.Trigger = None

        print 'Initialising programmable attenuator'
        if self.atten_hw == 'MC_RC4DAT6G95':
            self.ProgAtten = ProgrammableAttenuator.MC_RC4DAT6G95_Prog_Atten(
                ipaddress=self.all_devices['Programmable_attenuators'][self.atten_hw]['ipaddress'],
                port=self.all_devices['Programmable_attenuators'][self.atten_hw]['port'],
                timeout=self.all_devices['Programmable_attenuators'][self.atten_hw]['timeout']
                )
        elif self.atten_hw == 'Simulated':
            self.ProgAtten = ProgrammableAttenuator.Simulated_Prog_Atten()
        else:
            raise ValueError('You need a valid device name for the programmable attenuator')

        print 'Initialising BPM'
        if self.bpm_hw == 'Libera_Electron':
            self.BPM = BPMDevice.ElectronBPMDevice(epics_id=bpm_epics_id)
        elif self.bpm_hw == 'Libera_Brilliance':
            self.BPM = BPMDevice.BrillianceBPMDevice(epics_id=bpm_epics_id)
        elif self.bpm_hw == 'Simulated':
            self.BPM = BPMDevice.SimulatedBPMDevice(rf_sim=self.RF,
                                                    gatesim=self.GS,
                                                    progatten=self.ProgAtten,
                                                    noise_mag=self.all_devices['BPM'][self.bpm_hw]['noise_mag'],
                                                    damage_level=self.all_devices['BPM'][self.bpm_hw]['damage_level']
                                                    )
        else:
            raise ValueError('You need to select Libera Electron, Libera Brilliance or Simulated.')

        # Get device IDs
        self.rf_id = self.RF.get_device_id()
        self.bpm_id = self.BPM.get_device_id()
        self.prog_atten_id = self.ProgAtten.get_device_id()

        if gate_hw is not None:
            self.gate_id = self.GS.get_device_id()
        else:
            self.gate_id = None

        if trigger_hw is not None:
            self.trigger_id = self.Trigger.get_device_id()
        else:
            self.trigger_id = None

        # Set system losses
        """Adds information about system losses to the test system object"""
        self.channel_A_loss = 8.95
        self.channel_B_loss = 8.80
        self.channel_C_loss = 8.77
        self.channel_D_loss = 9.03
        """Returns the minimum loss between the RF source and the BPM input.
            This is required to make sure that nothing gets too much power 
            put into it, which would be a risk if the average was used."""
        self.loss = min(self.channel_A_loss, self.channel_B_loss,
                        self.channel_C_loss, self.channel_D_loss)
        """Maps ABCD to the programmable attenuator channels 1234.
        This depends on the wiring up of the test system."""
        self.channel_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1}

    def test_initialisation(self, test_name, frequency, output_power_level=-55):
        # Formats the test name and tells the user the test has started
        test_name = test_name.rsplit("Tests.")[1]
        test_name = test_name.replace("_", " ")
        print("Starting test \"" + test_name + "\"")

        # Initial setup of the RF system.
        self.RF.turn_off_RF()
        self.RF.set_frequency(frequency)
        max_system_output = self.rf_output - self.loss

        if output_power_level > self.BPM.damage_level:
            raise ValueError('Power level dangerously high')
        elif output_power_level > max_system_output:
            raise ValueError('Power level greater than system can provide')
        else:
            self.RF.set_output_power(self.rf_output)
            requested_attenuation = max_system_output - output_power_level
            self.ProgAtten.set_global_attenuation(requested_attenuation)
            atten = self.ProgAtten.get_global_attenuation()
            if atten[0] - atten[1] > 0.00001 or \
               atten[0] - atten[2] > 0.00001 or \
               atten[0] - atten[3] > 0.00001:
                raise ValueError('The attenuation values are not the same value')
            set_output_power = output_power_level + (requested_attenuation - atten[0])
        # Perform the test
        return test_name, set_output_power
