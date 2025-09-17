import unittest

import auth
from request_parsers import errors
from request_parsers.field_parsers import user_role as user_role_parser


class ParseUserRoleTest(unittest.TestCase):

    def test_rejects_non_strings(self):
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role(0)
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role(1)
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role(2)
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role(5.5)
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role(None)

    def test_rejects_empty_string(self):
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role('')

    def test_rejects_invalid_strings(self):
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role('')
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role('    ')
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role('admin')
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role('operator')
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role('SUPERADMIN')
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role('0')
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role('1')
        with self.assertRaises(errors.InvalidUserRoleError):
            user_role_parser.parse_user_role('2')

    def test_accepts_valid_strings(self):
        self.assertEqual(auth.Role.ADMIN,
                         user_role_parser.parse_user_role('ADMIN'))
        self.assertEqual(auth.Role.OPERATOR,
                         user_role_parser.parse_user_role('OPERATOR'))
