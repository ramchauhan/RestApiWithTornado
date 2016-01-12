import mock
import sqlite3
import unittest

from service import BaseHandler, DATABASE_NAME
from test_data import EMPLOYEE_DATA


class TestBaseHandler(unittest.TestCase):
    """
    test case for HomeHandler
    """
    def setUp(self):
        self.handlers = mock.MagicMock()
        self.settings = mock.MagicMock()
        self.database = {"database": DATABASE_NAME}
        self.home_handler = BaseHandler(self.handlers, self.settings, **self.database)
        self.database = mock.MagicMock()
        self.result = EMPLOYEE_DATA

    @mock.patch("sqlite3.connect")
    def test_initialize(self, mock_connect):
        self.home_handler.initialize(self.database)
        mock_connect.assert_called_once_with(self.database)

    def test_dict_builder(self):
        result = self.home_handler.dict_builder(self.result)
        self.assertEqual(result[0]['emp_id'], self.result[0][0])
        self.assertEqual(result[0]['first_name'], self.result[0][1])
        self.assertEqual(result[0]['zip'], self.result[0][-1])
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)

    def test_employee_obj(self):
        result = self.home_handler.employee_obj(self.result)
        self.assertEqual(result[0].emp_id, self.result[0][0])
        self.assertEqual(result[0].first_name, self.result[0][1])
        self.assertEqual(result[0].zip, self.result[0][-1])
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
