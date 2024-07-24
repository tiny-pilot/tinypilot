import network
import unittest
import subprocess
from unittest import mock


# This test checks the various potential JSON output values that the underlying
# `ip` command may return.
class InspectInterfaceTest(unittest.TestCase):

    @mock.patch.object(subprocess, 'check_output')
    def test_treats_empty_response_as_inactive_interface(self, mock_cmd):
        mock_cmd.return_value = ''
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, None, None)
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_treats_empty_array_as_inactive_interface(self, mock_cmd):
        mock_cmd.return_value = '[]'
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, None, None)
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_treats_emtpy_object_as_inactive_interface(self, mock_cmd):
        mock_cmd.return_value = '[{}]'
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, None, None)
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_disregards_command_failure(self, mock_cmd):
        mock_cmd.side_effect = mock.Mock(
            side_effect=subprocess.CalledProcessError(returncode=1, cmd='ip'))
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, None, None)
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_operstate_down_as_not_connected(self, mock_cmd):
        mock_cmd.return_value = """
            [{"operstate":"DOWN"}]
        """
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, None, None)
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_operstate_up_as_connected(self, mock_cmd):
        mock_cmd.return_value = """
            [{"operstate":"UP"}]
        """
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(True, None, None)
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_mac_address(self, mock_cmd):
        mock_cmd.return_value = """
            [{"address":"00-b0-d0-63-c2-26"}]
        """
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, None, '00-b0-d0-63-c2-26')
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_normalizes_mac_address_to_use_dashes(self, mock_cmd):
        mock_cmd.return_value = """
            [{"address":"00:b0:d0:63:c2:26"}]
        """
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, None, '00-b0-d0-63-c2-26')
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_ip_address(self, mock_cmd):
        mock_cmd.return_value = """
            [{"addr_info":[{"family":"inet","local":"192.168.2.5"}]}]
        """
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, "192.168.2.5", None)
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_disregards_other_families_such_as_ipv6(self, mock_cmd):
        mock_cmd.return_value = """
            [{"addr_info":[{"family":"inet6","local":"::ffff:c0a8:205"}]}]
        """
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, None, None)
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_parses_all_data(self, mock_cmd):
        mock_cmd.return_value = """
            [{
                "operstate":"UP",
                "address":"00-b0-d0-63-c2-26",
                "addr_info":[{"family":"inet","local":"192.168.2.5"}]
            }]
        """
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(True, "192.168.2.5",
                                           "00-b0-d0-63-c2-26")
        self.assertEqual(interface_status, expected)

    @mock.patch.object(subprocess, 'check_output')
    def test_disregards_invalid_json(self, mock_cmd):
        mock_cmd.return_value = '[{"address'
        interface_status = network._inspect_interface('eth0')
        expected = network.InterfaceStatus(False, None, None)
        self.assertEqual(interface_status, expected)
