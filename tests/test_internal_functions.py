import unittest
from FritzHome import FritzHome, Device, DeviceNotFoundError
import xml.etree.ElementTree as ET
from itertools import product


class InternalFunctionsTests(unittest.TestCase):

    def test_parse_device_infos(self):
        with open('device_infos.xml', 'r') as input_file:
            xml = input_file.read()
        devices = FritzHome._parse_device_infos(ET.fromstring(xml))
        self.assertIn(Device('10001 1000001', 'Contact 1', []), devices)
        self.assertIn(Device('10001 1000001-1', 'Contact1a', ['alert']), devices)
        self.assertIn(Device('10002 1000002', 'Switch 1', ['switch', 'powermeter', 'temperature']), devices)
        self.assertIn(Device('10004 1000004', 'Switch 2', ['switch', 'powermeter', 'temperature']), devices)
        self.assertIn(Device('10003 1000003', 'TRV 1', ['temperature', 'hkr']), devices)
        self.assertIn(Device('10005 1000005', 'Button 1', []), devices)

    def test_generate_challenge_answer(self):
        challenge = 'abcdef12345'
        password = 'qk1xtp/ev'
        answer = FritzHome._generate_challenge_answer(challenge, password)
        self.assertEqual(answer, 'abcdef12345-14a13734d967552130a29e9d04375773')

    def test_convert_temperature(self):
        t_from_list = [(20, 'celsius'),
                       (200, 'decidegrees celsius'),
                       (40, 'halfdegrees celsius')]
        t_to_list = [(20, 'celsius'),
                     (68, 'fahrenheit'),
                     (40, 'halfdegrees celsius'),
                     (293.15, 'kelvin')]
        for (t_from, unit_from), (t_to, unit_to) in product(t_from_list, t_to_list):
            self.assertAlmostEqual(
                t_to, FritzHome._convert_temperature(t_from, unit_from, unit_to), 2)

    def test_get_ain_by_name(self):
        fh = FritzHome()
        small_green_button = Device('42', 'small green button', [])
        big_red_button = Device('007', 'big red button', [])
        fh.devices = [small_green_button, big_red_button]
        device_ain = fh._get_ain_by_name('big red button')
        self.assertEqual('007', device_ain)

    def test_device_not_found_with_empty_list(self):
        fh = FritzHome()
        with self.assertRaises(DeviceNotFoundError) as error_context:
            fh._get_ain_by_name('big red button')
        self.assertEqual('Device not found: "big red button"', str(error_context.exception))

    def test_device_not_found_with_wrong_devices(self):
        fh = FritzHome()
        fh.devices = [Device('42', 'small green button', [])]
        with self.assertRaises(DeviceNotFoundError) as error_context:
            fh._get_ain_by_name('big red button')
        self.assertEqual('Device not found: "big red button"', str(error_context.exception))
