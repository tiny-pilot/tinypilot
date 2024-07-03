import unittest
from unittest import mock

from request_parsers import errors
from request_parsers import network


def make_mock_request(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class NetworkValidationTest(unittest.TestCase):

    def test_accepts_valid_wifi_credentials_with_psk(self):
        wifi = network.parse_wifi_settings(
            make_mock_request({
                'countryCode': 'US',
                'ssid': 'my-network',
                'psk': 's3cr3t!!!'
            }))
        self.assertEqual('US', wifi.country_code)
        self.assertEqual('my-network', wifi.ssid)
        self.assertEqual('s3cr3t!!!', wifi.psk)

    def test_accepts_valid_wifi_credentials_without_psk(self):
        wifi = network.parse_wifi_settings(
            make_mock_request({
                'countryCode': 'DE',
                'ssid': 'SomeWiFiHotspot_123',
                'psk': None
            }))
        self.assertEqual('DE', wifi.country_code)
        self.assertEqual('SomeWiFiHotspot_123', wifi.ssid)
        self.assertEqual(None, wifi.psk)

    def test_normalizes_country_code_to_uppercase(self):
        wifi = network.parse_wifi_settings(
            make_mock_request({
                'countryCode': 'us',
                'ssid': 'SomeWiFiHotspot_123',
                'psk': None
            }))
        self.assertEqual('US', wifi.country_code)

    def test_rejects_absent_required_fields(self):
        with self.assertRaises(errors.MissingFieldError):
            network.parse_wifi_settings(
                make_mock_request({
                    'ssid': 'my-network',
                    'psk': 's3cr3t!!!'
                }))
        with self.assertRaises(errors.MissingFieldError):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'US',
                    'psk': 's3cr3t!!!'
                }))
        with self.assertRaises(errors.MissingFieldError):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'US',
                    'ssid': 'my-network'
                }))

    def test_rejects_country_code_with_incorrect_type(self):
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 12,
                    'ssid': 'my-network',
                    'psk': 's3cr3t!!!'
                }))
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': None,
                    'ssid': 'my-network',
                    'psk': 's3cr3t!!!'
                }))

    def test_rejects_country_code_with_incorrect_length(self):
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'A',
                    'ssid': 'my-network',
                    'psk': 's3cr3t!!!'
                }))
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'ABC',
                    'ssid': 'my-network',
                    'psk': 's3cr3t!!!'
                }))

    def test_rejects_country_code_non_alpha(self):
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': '12',
                    'ssid': 'my-network',
                    'psk': 's3cr3t!!!'
                }))
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'A*',
                    'ssid': 'my-network',
                    'psk': 's3cr3t!!!'
                }))

    def test_rejects_ssid_with_incorrect_type(self):
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'US',
                    'ssid': 123,
                    'psk': 's3cr3t!!!'
                }))
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'US',
                    'ssid': None,
                    'psk': 's3cr3t!!!'
                }))

    def test_rejects_psk_with_incorrect_type(self):
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'US',
                    'ssid': 'my-network',
                    'psk': 123,
                }))

    def test_rejects_ssid_with_incorrect_length(self):
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'US',
                    'ssid': '',
                    'psk': 's3cr3t!!!'
                }))

    def test_rejects_psk_with_incorrect_length(self):
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'US',
                    'ssid': 'Hotspot123',
                    'psk': 'x' * 7
                }))
        with self.assertRaises(errors.InvalidWifiSettings):
            network.parse_wifi_settings(
                make_mock_request({
                    'countryCode': 'US',
                    'ssid': 'Hotspot123',
                    'psk': 'x' * 64
                }))
