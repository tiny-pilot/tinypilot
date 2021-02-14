import unittest

import hostname


class HostnameTest(unittest.TestCase):

    def test_parses_the_hostname_out_of_etc_hostname_file(self):
        etc_hostname = '# Some comment\n \n hostname \n'
        self.assertEqual('hostname', hostname.parse_etc_hostname(etc_hostname))
