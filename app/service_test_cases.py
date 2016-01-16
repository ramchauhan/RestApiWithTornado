try:
    import simplejson as json
except ImportError:
    import json
import mock
import unittest

from service import BaseHandler, EmployeeHandler, HomeHandler, DATABASE_NAME
from test_data import EMPLOYEE_DATA, POST_DATA


class TestBaseHandler(unittest.TestCase):
    """
    test case for BaseHandler
    """
    def setUp(self):
        self.handlers = mock.MagicMock()
        self.settings = mock.MagicMock()
        self.database = {"database": DATABASE_NAME}
        self.base_handler = BaseHandler(self.handlers, self.settings, **self.database)
        self.database = mock.MagicMock()
        self.result = EMPLOYEE_DATA

    @mock.patch("sqlite3.connect")
    def test_initialize(self, mock_connect):
        """
        test case for method initialize
        :param mock_connect:
        :return:
        """
        self.base_handler.initialize(self.database)
        mock_connect.assert_called_once_with(self.database)

    def test_dict_builder(self):
        """
        test case for method dict_builder
        :return:
        """
        result = self.base_handler.dict_builder(self.result)
        self.assertEqual(result[0]['emp_id'], self.result[0][0])
        self.assertEqual(result[0]['first_name'], self.result[0][1])
        self.assertEqual(result[0]['zip'], self.result[0][-1])
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)

    def test_employee_obj(self):
        """
        test case for method employee_obj
        :return:
        """
        result = self.base_handler.employee_obj(self.result)
        self.assertEqual(result[0].emp_id, self.result[0][0])
        self.assertEqual(result[0].first_name, self.result[0][1])
        self.assertEqual(result[0].zip, self.result[0][-1])
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)


class TestHomeHandler(unittest.TestCase):
    """
    test case for HomeHandler
    """
    def setUp(self):
        self.handlers = mock.MagicMock()
        self.settings = mock.MagicMock()
        self.database = {"database": DATABASE_NAME}
        self.home_handler = HomeHandler(self.handlers, self.settings, **self.database)

    def test_get(self):
        """
        test case for method get
        """
        self.home_handler.cursor = mock.MagicMock()
        self.home_handler.render = mock.MagicMock()
        self.home_handler.employee_obj = mock.MagicMock()
        self.home_handler.db = mock.MagicMock()
        self.home_handler.get()
        self.home_handler.cursor.execute.assert_called_once_with('SELECT * FROM employee')
        self.home_handler.db.commit.assert_called_with()
        self.home_handler.db.close.assert_called_with()
        self.home_handler.cursor.fetchall.assert_called_with()


class TestEmployeeHandler(unittest.TestCase):
    """
    test case for EmployeeHandler
    """
    def setUp(self):
        self.handlers = mock.MagicMock()
        self.settings = mock.MagicMock()
        self.database = {"database": DATABASE_NAME}
        self.emp_handler = EmployeeHandler(self.handlers, self.settings, **self.database)
        self.result = EMPLOYEE_DATA
        self.emp_id = EMPLOYEE_DATA[0][0]
        self.emp_handler.dict_builder = mock.MagicMock()
        self.emp_handler.db = mock.MagicMock(return_value="successfully connected")
        self.emp_handler.cursor = mock.MagicMock()
        self.emp_handler.cursor.fetchone.return_value = self.result[0]

    def test_validate_data_ok(self):
        data = json.loads(POST_DATA)
        self.emp_handler.validate_data(POST_DATA)
        self.assertEqual(self.emp_handler.data, data)

    def test_get_with_data(self):
        """
        Test case when there data exist for the requested emp_id
        :return:
        """
        self.emp_handler.get(self.emp_id)
        self.emp_handler.cursor.execute.assert_called_once_with('''SELECT * from employee where emp_id=?''', self.emp_id)
        self.emp_handler.dict_builder.assert_called_once_with(self.result)
        self.assertEqual(self.emp_handler._status_code, 200)

    def test_get_with_no_data(self):
        """
        Test case when there is no data for the requested emp_id
        :return:
        """
        self.emp_handler.cursor.fetchone.return_value = []
        self.emp_handler.get(self.emp_id)
        self.emp_handler.cursor.execute.assert_called_once_with('''SELECT * from employee where emp_id=?''', self.emp_id)
        self.assertEqual(self.emp_handler._status_code, 404)

    def test_get_with_attribute_error(self):
        """
        test case for AttributeError
        :return:
        """
        self.emp_handler.cursor.execute.side_effect = AttributeError()
        self.emp_handler.get(self.emp_id)
        self.emp_handler.cursor.execute.assert_called_once_with('''SELECT * from employee where emp_id=?''', self.emp_id)
        self.assertEqual(self.emp_handler._status_code, 404)

    def test_post(self):
        """
        Test case for post method
        :return:
        """
        self.emp_handler.request = mock.MagicMock()
        self.emp_handler.request.body = POST_DATA
        self.emp_handler.validate_data = mock.MagicMock(return_value=True)
        self.emp_handler.data = json.loads(POST_DATA)
        self.emp_handler.post()
        self.emp_handler.cursor.execute.assert_called_once_with("INSERT INTO employee(first_name, last_name, address, "
                                                                "city, state, zip) VALUES(?,?,?,?,?,?)",
                                                                (self.emp_handler.data['first_name'],
                                                                 self.emp_handler.data.get('last_name'),
                                                                 self.emp_handler.data.get('address'),
                                                                 self.emp_handler.data.get('city'),
                                                                 self.emp_handler.data.get('state'),
                                                                 self.emp_handler.data['zip']))
        self.emp_handler.validate_data.assert_called_once_with(POST_DATA)
        self.assertEqual(self.emp_handler._status_code, 201)

    def test_put(self):
        """
        Test case for put method
        :return:
        """
        self.emp_handler.request = mock.MagicMock()
        self.emp_handler.request.body = POST_DATA
        self.emp_handler.validate_data = mock.MagicMock(return_value=True)
        self.emp_handler.data = json.loads(POST_DATA)
        self.emp_handler.put(self.emp_id)
        self.emp_handler.cursor.execute.assert_called_once_with("UPDATE employee set first_name=?, last_name=?, "
                                                                "address=?, city=?, state=?, zip=? "
                                                                " WHERE emp_id=?", (self.emp_handler.data['first_name'],
                                                                                    self.emp_handler.data.get('last_name'),
                                                                                    self.emp_handler.data.get('address'),
                                                                                    self.emp_handler.data.get('city'),
                                                                                    self.emp_handler.data.get('state'),
                                                                                    self.emp_handler.data['zip'],
                                                                                    int(self.emp_id)))
        self.emp_handler.validate_data.assert_called_once_with(POST_DATA)
        self.assertEqual(self.emp_handler._status_code, 201)

    def test_delete(self):
        """
        Test case for delete method
        :return:
        """
        self.emp_handler.delete(self.emp_id)
        self.emp_handler.cursor.execute.assert_called_once_with('''DELETE from employee where emp_id=?''', self.emp_id)
        self.assertEqual(self.emp_handler._status_code, 200)


if __name__ == "__main__":
    unittest.main()
