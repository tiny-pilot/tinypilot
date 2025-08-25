import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import network


# This test checks the various potential JSON output values that the underlying
# `ip` command may return.
class InspectInterfaceTest(unittest.TestCase):

    @mock.patch.object(subprocess, 'check_output')
    def test_treats_empty_response_as_inactive_interface(self, mock_cmd):
        mock_cmd.return_value = ''
        self.assertEqual(
            network.InterfaceStatus('eth0', False, None, None),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_treats_empty_array_as_inactive_interface(self, mock_cmd):
        mock_cmd.return_value = '[]'
        self.assertEqual(
            network.InterfaceStatus('eth0', False, None, None),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_treats_emtpy_object_as_inactive_interface(self, mock_cmd):
        mock_cmd.return_value = '[{}]'
        self.assertEqual(
            network.InterfaceStatus('eth0', False, None, None),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_disregards_command_failure(self, mock_cmd):
        mock_cmd.side_effect = mock.Mock(
            side_effect=subprocess.CalledProcessError(returncode=1, cmd='ip'))
        self.assertEqual(
            network.InterfaceStatus('eth0', False, None, None),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_operstate_down_as_not_connected(self, mock_cmd):
        mock_cmd.return_value = """
            [{"operstate":"DOWN"}]
        """
        self.assertEqual(
            network.InterfaceStatus('eth0', False, None, None),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_operstate_up_as_connected(self, mock_cmd):
        mock_cmd.return_value = """
            [{"operstate":"UP"}]
        """
        self.assertEqual(
            network.InterfaceStatus('eth0', True, None, None),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_mac_address(self, mock_cmd):
        mock_cmd.return_value = """
            [{"address":"00-b0-d0-63-c2-26"}]
        """
        self.assertEqual(
            network.InterfaceStatus('eth0', False, None, '00-b0-d0-63-c2-26'),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_normalizes_mac_address_to_use_dashes(self, mock_cmd):
        mock_cmd.return_value = """
            [{"address":"00:b0:d0:63:c2:26"}]
        """
        self.assertEqual(
            network.InterfaceStatus('eth0', False, None, '00-b0-d0-63-c2-26'),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_ip_address(self, mock_cmd):
        mock_cmd.return_value = """
            [{"addr_info":[{"family":"inet","local":"192.168.2.5"}]}]
        """
        self.assertEqual(
            network.InterfaceStatus('eth0', False, '192.168.2.5', None),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_disregards_other_families_such_as_ipv6(self, mock_cmd):
        mock_cmd.return_value = """
            [{"addr_info":[{"family":"inet6","local":"::ffff:c0a8:205"}]}]
        """
        self.assertEqual(
            network.InterfaceStatus('eth0', False, None, None),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_all_data(self, mock_cmd):
        mock_cmd.return_value = """
            [{
                "operstate":"UP",
                "address":"00-b0-d0-63-c2-26",
                "addr_info":[{"family":"inet","local":"192.168.2.5"}]
            }]
        """
        self.assertEqual(
            network.InterfaceStatus('eth0', True, '192.168.2.5',
                                    '00-b0-d0-63-c2-26'),
            network.inspect_interface('eth0'),
        )

    @mock.patch.object(subprocess, 'check_output')
    def test_disregards_invalid_json(self, mock_cmd):
        mock_cmd.return_value = '[{"address'
        self.assertEqual(
            network.InterfaceStatus('eth0', False, None, None),
            network.inspect_interface('eth0'),
        )


class GetNetworkInterfacesTest(unittest.TestCase):

    def test_returns_empty_list_when_path_is_not_a_directory(self):
        with tempfile.NamedTemporaryFile() as mock_file:
            with mock.patch.object(network, '_INTERFACES_DIR', mock_file.name):
                self.assertEqual([], network.get_network_interfaces())

    def test_returns_empty_list_when_path_does_not_exist(self):
        with tempfile.TemporaryDirectory() as mock_dir:
            with mock.patch.object(network, '_INTERFACES_DIR',
                                   f'{mock_dir}/path/does/not/exist'):
                self.assertEqual([], network.get_network_interfaces())

    def test_returns_empty_list_when_directory_has_no_interfaces(self):
        with tempfile.TemporaryDirectory() as mock_dir:
            with mock.patch.object(network, '_INTERFACES_DIR', mock_dir):
                self.assertEqual([], network.get_network_interfaces())

    def test_excludes_loopback_and_virtual_interfaces(self):
        with tempfile.TemporaryDirectory() as mock_dir:
            mock_net_interfaces_dir = Path(mock_dir)
            # Physical interfaces (with 'device').
            (mock_net_interfaces_dir / 'eth0' / 'device').mkdir(parents=True)
            (mock_net_interfaces_dir / 'wlan0' / 'device').mkdir(parents=True)
            # Loopback (no 'device' in the path).
            (mock_net_interfaces_dir / 'lo').mkdir()
            # Some virtual interface (no 'device' in the path).
            (mock_net_interfaces_dir / 'veth0').mkdir()
            with mock.patch.object(network, '_INTERFACES_DIR',
                                   str(mock_net_interfaces_dir)):
                self.assertEqual(['eth0', 'wlan0'],
                                 network.get_network_interfaces())

    def test_returns_sorted_interface_names(self):
        with tempfile.TemporaryDirectory() as mock_dir:
            mock_net_interfaces_dir = Path(mock_dir)
            # Create in unsorted order.
            (mock_net_interfaces_dir / 'wlan0' / 'device').mkdir(parents=True)
            (mock_net_interfaces_dir / 'eth0' / 'device').mkdir(parents=True)
            with mock.patch.object(network, '_INTERFACES_DIR',
                                   str(mock_net_interfaces_dir)):
                self.assertEqual(['eth0', 'wlan0'],
                                 network.get_network_interfaces())
