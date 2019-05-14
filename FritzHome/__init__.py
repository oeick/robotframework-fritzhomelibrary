import requests
import xml.etree.ElementTree as ET
import hashlib
from typing import List, Union
from dataclasses import dataclass
from robot.api.deco import keyword
from robot.api import logger

NO_SESSION = '0000000000000000'
KNOWN_FUNCTIONS = ['alert', 'switch', 'powermeter', 'temperature', 'hkr']


@dataclass
class Device:
    ain: str
    name: str
    functions: List[str]


class FritzHome:
    """
    FritzHome Library for the Robot Framework provides keywords to access the
    home automation devices of the Fritz!BOX from AVM.

    It accesses the home automation http interface and hides this technical part,
    so that the keywords can be used without worrying about a session ID or AIN.

    Just import this library into a robot testsuite or a robot task:
    | *** Settings *** |
    | Library          | FritzHome |

    Example: Switching on a Fritz!DECT 200 switch:
    | Open Session     | my_password       | my_username |
    | Set Switch State | name_of_my_switch | On          |

    Example: Getting the temperature measured by a home automation device
    | Open Session              | ${password}     | ${username}       |
    | ${temperature_celsius}    | Get Temperature | name_of_the_device |
    | ${temperature_fahrenheit} | Get Temperature | name_of_the_device | Fahrenheit |
    | ${temperature_kelvin}     | Get Temperature | name_of_the_device | Kelvin     |
    """

    ROBOT_LIBRARY_VERSION = '0.1.0'
    ROBOT_LIBRARY_SCOPE = 'TEST CASE'

    is_session_open: bool
    session_id: str
    login_url: str
    homeautoswitch_url: str
    devices: List[Device]

    def __init__(self):
        self.is_session_open = False
        self.session_id = ''
        self.login_url = ''
        self.homeautoswitch_url = ''
        self.devices = []

    def _get_infos_of_all_devices(self) -> List[Device]:
        """ Asks the fritzbox for information about all home automation devices. """
        device_infos_xml: ET.Element = self._send_switch_command('getdevicelistinfos', response_format='xml')
        return self._parse_device_infos(device_infos_xml)

    @staticmethod
    def _parse_device_infos(device_infos: ET.Element) -> List[Device]:
        """
        Parses some information from the given xml data about home automation devices of the fritzbox.
        Returns a list of ``Device`` objects.
        """
        devices_xml = device_infos.findall(f'device')
        devices = []
        for device in devices_xml:
            devices.append(Device(
                name=device.find('name').text,
                ain=device.attrib['identifier'],
                functions=[f.tag for f in device.findall('./') if f.tag in KNOWN_FUNCTIONS]
            ))
        return devices

    def _answer_the_challenge(self, challenge: str, password: str, username: str) -> str:
        challenge_response = self._generate_challenge_answer(challenge, password)
        content_xml = FritzHome._send_command(
            url=self.login_url,
            response_format='xml',
            username=username,
            response=challenge_response)
        session_id = content_xml.findtext('./SID')
        return session_id

    @staticmethod
    def _generate_challenge_answer(challenge: str, password: str) -> str:
        encoded_answer = hashlib.md5()
        encoded_answer.update(challenge.encode('utf-16le'))
        encoded_answer.update('-'.encode('utf-16le'))
        encoded_answer.update(password.encode('utf-16le'))
        challenge_response = f'{challenge}-{encoded_answer.hexdigest()}'
        return challenge_response

    @staticmethod
    def _send_command(url, response_format: str = 'plain', **params):
        response = requests.get(url, params)
        if response.status_code == 400:
            raise UnknownCommandError(f'FritzBox does not recognize the command. Parameters were: "{params}"')
        content_utf8 = response.content.decode('utf-8')
        if response_format == 'plain':
            return content_utf8.strip()
        elif response_format == 'xml':
            return ET.fromstring(content_utf8)

    def _send_switch_command(self, command: str, response_format: str = 'plain', **params) -> Union[str, ET.Element]:
        get_params = {'switchcmd': command, 'sid': self.session_id, **params}
        return self._send_command(self.homeautoswitch_url, response_format, **get_params)

    def _get_ain_by_name(self, device_name):
        found_device = next((d for d in self.devices if d.name == device_name), None)
        if not found_device:
            raise DeviceNotFoundError(f'Device not found: "{device_name}"')
        return found_device.ain

    @staticmethod
    def _convert_temperature(value: float, source_unit: str, target_unit: str):
        temperature_kelvin = {
            'celsius': lambda t: t + 273.15,
            'decidegrees celsius': lambda t: t / 10 + 273.15,
            'halfdegrees celsius': lambda t: t / 2 + 273.15,
        }[source_unit](value)
        return {
            'celsius': lambda t: t - 273.15,
            'fahrenheit': lambda t: t * 1.8 - 459.67,
            'halfdegrees celsius': lambda t: (t - 273.15) * 2,
            'kelvin': lambda t: t
        }[target_unit](temperature_kelvin)

    @keyword
    def open_session(self, password: str, username: str = 'admin', url: str = 'http://fritz.box'):
        """
        Starts a new fritzbox session.

        Default ``username`` is 'admin' and default ``url`` is 'http://fritz.box'.

        See also ``Close Session``
        """
        if self.is_session_open:
            logger.warn('Session was already opened, but new session will be created anyway.')
        self.login_url = f'{url}/login_sid.lua'
        self.homeautoswitch_url = f'{url}/webservices/homeautoswitch.lua'
        content_xml = FritzHome._send_command(url=self.login_url, response_format='xml')
        session_id = content_xml.findtext('./SID')
        challenge = content_xml.findtext('./Challenge')

        if session_id == NO_SESSION:
            session_id = self._answer_the_challenge(challenge, password, username)

        if session_id == NO_SESSION:
            raise PermissionError('Access to home automation interface denied.')

        self.session_id = session_id
        self.is_session_open = True
        self.devices = self._get_infos_of_all_devices()

    @keyword
    def get_all_devices(self) -> List[str]:
        """ Returns a list with names of all devices from the opened session."""
        return [d.name for d in self.devices]

    @keyword
    def get_all_switches(self) -> List[str]:
        """ Returns a list with names of all switches from the opened session."""
        return [d.name for d in self.devices if 'switch' in d.functions]

    @keyword(name='Get All TRV')
    def get_all_trv(self) -> List[str]:
        """ Returns a list with names of all thermostatic radiator valves from the opened session."""
        return [d.name for d in self.devices if 'hkr' in d.functions]

    @keyword
    def get_all_alerts(self) -> List[str]:
        """ Returns a list with names of all alert devices from the opened session."""
        return [d.name for d in self.devices if 'alert' in d.functions]

    @keyword
    def close_session(self):
        """
        Closes the session with the fritzbox.

        See also ``Open Session``
        """
        if not self.is_session_open:
            logger.warn('There was no open session to close.')
        self.is_session_open = False
        self.session_id = ''
        self.login_url = ''
        self.homeautoswitch_url = ''
        self.devices = []

    @keyword(name='Get Session ID')
    def get_session_id(self) -> str:
        """ Returns the fritzbox session ID of the opened session. """
        return self.session_id

    @keyword
    def set_switch_state(self, switch: str, state: str) -> str:
        """
        Sets a switch to on or off. Accepted states are ``On``, ``Off`` and ``Toggle``.

        Returns the new state.
        """
        if state.lower() not in ('on', 'off', 'toggle'):
            raise SyntaxError(f'Unknown switch mode: "{state}".')
        returned_state = self._send_switch_command(f'setswitch{state.lower()}', ain=self._get_ain_by_name(switch))
        return {'0': 'Off', '1': 'On'}[returned_state.strip()]

    @keyword
    def get_switch_state(self, switch: str) -> str:
        """ Returns the state of the given switch: ``On``, ``Off`` or ``Unknown``."""
        returned_state = self._send_switch_command('getswitchstate', ain=self._get_ain_by_name(switch))
        return {'0': 'Off', '1': 'On', 'inval': 'Unknown'}[returned_state]

    @keyword
    def is_switch_present(self, switch: str) -> bool:
        """ Returns ``True`` if the switch is connected to the fritzbox, ``False`` otherwise."""
        presence = self._send_switch_command('getswitchpresent', ain=self._get_ain_by_name(switch))
        return presence == '1'

    @keyword
    def get_switch_power(self, switch: str) -> str:
        """ Returns the power measured by the given switch in milliwatt (mW)."""
        power = self._send_switch_command('getswitchpower', ain=self._get_ain_by_name(switch))
        return power

    @keyword
    def get_switch_energy(self, switch: str) -> str:
        """
        Returns the energy gone through the given switch since first commissioning,
        or since last reset of the energy statistic. Unit is watt hours.
        """
        energy = self._send_switch_command('getswitchenergy', ain=self._get_ain_by_name(switch))
        return energy

    @keyword(name='Get AIN')
    def get_ain(self, devicename: str) -> str:
        """
        Returns the AIN of the device with the given name.

        The AIN identifies the device internally.
        Generally the AIN can be the identification number of an actuator, a template or a MAC address.

        Usually the AIN is not needed for the keywords of this library, because most keywords use the
        name instead.
        """
        return self._get_ain_by_name(devicename)

    @keyword
    def get_temperature(self, devicename: str, unit='celsius') -> float:
        """
        Returns the temperature measured by the device with the given name.
        Possible unites (case insensitive):
          - ``Celsius`` for degree Celsius (°C), default
          - ``Fahrenheit`` for degree Fahrenheit (°F)
          - ``Kelvin`` for Kelvin (K)
        """
        temperature = float(self._send_switch_command('gettemperature', ain=self._get_ain_by_name(devicename)))
        return self._convert_temperature(temperature, source_unit='decidegrees celsius', target_unit=unit.lower())

    @keyword
    def send_direct_command(self, command: str, **kwargs) -> str:
        """
        Sends the given command directly to the fritzbox.
        All given keyword arguments will be appended to the command url.

        This is for the case, that a function is needed that is not covert by the keywords of this library.

        Example:
        | Send Direct Command | setswitchoff | ain=087610485036 |
        The above example sets the state of the switch to ``Off``, similar to the
        keyword ``Set Switch State``, but uses the AIN instead of the name.
        """
        response = self._send_switch_command(command, **kwargs)
        return response

    @keyword
    def get_alert_state(self, alertname: str) -> str:
        """
        Gets the alert state of the device with the given name.
        """
        device_infos_xml = self._send_switch_command('getdevicelistinfos', response_format='xml')
        alert_device = device_infos_xml.find(f'device/name[.="{alertname}"]/../alert/state')
        if alert_device is None or not isinstance(alert_device, ET.Element):
            raise DeviceNotFoundError(f'Found no alert device "{alertname}"')
        state = alert_device.text
        return state

    @keyword(name='Get TRV Setpoint')
    def get_trv_setpoint(self, trvname: str, unit: str = 'celsius') -> str:
        """
        Returns the setpoint of the TRV (thermostatic radiator valve) with the given name.

        The setpoint is the temperature to be reached by the radiator.
        """
        temperature = float(self._send_switch_command('gethkrtsoll', ain=self._get_ain_by_name(trvname)).strip())
        return self._convert_temperature(temperature, 'halfdegrees celsius', unit)

    @keyword(name='Get TRV Comfort')
    def get_trv_comfort(self, trvname: str, unit: str = 'celsius') -> str:
        """
        Returns the comfort temperature of the TRV (thermostatic radiator valve) with the given name.

        The comfort temperature and the low temperature are set by fritzbox configuration.
        """
        temperature = float(self._send_switch_command('gethkrkomfort', ain=self._get_ain_by_name(trvname)).strip())
        return self._convert_temperature(temperature, 'halfdegrees celsius', unit)

    @keyword(name='Get TRV Low')
    def get_trv_low(self, trvname: str, unit: str = 'celsius') -> str:
        """
        Returns the low temperature of the TRV (thermostatic radiator valve) with the given name.

        The comfort temperature and the low temperature are set by fritzbox configuration.
        """
        temperature = float(self._send_switch_command('gethkrabsenk', ain=self._get_ain_by_name(trvname)).strip())
        return self._convert_temperature(temperature, 'halfdegrees celsius', unit)

    @keyword(name='Set TRV Setpoint')
    def set_trv_setpoint(self, trvname: str, temperature: Union[float, str], unit: str = 'celsius'):
        """
        Sets the temperature to be reached by the radiator.

        Setpoint temperature can be replaced by the fritzbox with comfort or low temperature, if configured so.

        Changes to the TRV can take up to 15 minutes to have effect.
        """
        temperature = self._convert_temperature(float(temperature), unit, 'halfdegrees celsius')
        self._send_switch_command('sethkrtsoll', ain=self._get_ain_by_name(trvname), param=str(temperature)).strip()


class UnknownCommandError(Exception):
    pass


class DeviceNotFoundError(Exception):
    pass
