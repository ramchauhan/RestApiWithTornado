import logging
import os
try:
    import simplejson as json
except ImportError:
    import json
import sqlite3
import collections

from tornado.ioloop import IOLoop
import tornado.web

DATABASE_NAME = "employee.db"


class InitializeDatabase(object):
    """
    Sqlite3 database creation if not exist
    """
    def __init__(self):
        self.db = sqlite3.connect(DATABASE_NAME)
        cursor = self.db.cursor()
        try:
            cursor.execute('SELECT * FROM employee')
        except sqlite3.OperationalError:
            cursor.execute('CREATE TABLE employee (\
                emp_id INTEGER PRIMARY KEY AUTOINCREMENT,\
                first_name text NOT NULL,\
                last_name text,\
                address CHAR(255),\
                city text,\
                state text,\
                zip INTEGER NOT NULL)')
            logging.info("database crated successfully")
        self.db.commit()
        self.db.close()


class BaseHandler(tornado.web.RequestHandler):
    """
    Base class handler for the db initialization and making dict of employee data
    """
    def initialize(self, database):
        if database != DATABASE_NAME:
            self.write("Not a valid database name")
        self.db = sqlite3.connect(database)
        self.cursor = self.db.cursor()

    def dict_builder(self, result):
        """
        make the dict as per table structure
        :param result:
        :return:
        """
        item_dict = []
        for item in result:
            item_dict.append({
                "emp_id": item[0],
                "first_name": item[1],
                "last_name": item[2],
                "address": item[3],
                "city": item[4],
                "state": item[5],
                "zip": item[6]
            })
        return item_dict

    def employee_obj(self, result):
        """
        make the employee object by using named tuple
        This is example where we are using namedtuple
        :param result:
        :return:
        """
        employee_dict = []
        for item in result:
            employee = collections.namedtuple("Employee", "emp_id first_name last_name address city state zip")
            employee.emp_id = item[0]
            employee.first_name = item[1]
            employee.last_name = item[2]
            employee.address = item[3]
            employee.city = item[4]
            employee.state = item[5]
            employee.zip = item[6]

            employee_dict.append(employee)

        return employee_dict


class HomeHandler(BaseHandler):
    """
    Home page handler
    """
    def get(self):
        self.cursor.execute('SELECT * FROM employee')
        result = self.cursor.fetchall()
        employees = self.employee_obj(result)
        self.render("home.html", title="My title", employees=employees)
        self.db.commit()
        self.db.close()


class EmployeeHandler(BaseHandler):
    """
    Class to represent handle all CRUD operations
    """
    def validate_data(self, data):
        """
        validate the input data for the service purpose
        :param data:
        :return:
        """
        try:
            self.data = json.loads(data)
            if not self.data.get('first_name') and not self.data.get('zip'):
                self.write("both, first_name and zip or mandatory fields")
                # setting bad request
                self.set_status(400)
                logging.error("json is not having proper keys")
                return
            elif not self.data.get('first_name'):
                self.write("first_name, is mandatory fields")
                # setting bad request
                self.set_status(400)
                logging.error("json is not having proper keys")
                return
            elif not self.data.get('zip'):
                self.write("zip, is mandatory fields")
                # setting bad request
                self.set_status(400)
                logging.error("json is not having proper keys")
                return
        except json.decoder.JSONDecodeError:
            self.write("bad data, not able to decode")
            # setting bad request
            self.set_status(400)
            logging.error("json is not proper")
            return
        return True

    def get(self, emp_id):
        """
        method to handle the GET request from the client
        :param emp_id:
        :return:
        """
        try:
            self.cursor.execute('''SELECT * from employee where emp_id=?''', emp_id)
            emp = self.cursor.fetchone()
            if not emp:
                self.db.close()
                self.write("There are no record to display")
                self.set_status(404)
                # here need to think what i have to return
                return
            self.db.close()
            emp_data = self.dict_builder([emp])
            self.set_header('Content-Type', 'application/json')
            self.set_status(200)
            self.write(json.dumps(emp_data))
        except AttributeError:
            self.db.close()
            self.set_status(404)
            self.write("There are no record to display")
            return

    def post(self):
        """
        method to handle the POST request from the client
        :return:
        """
        body_data = self.request.body
        if not self.validate_data(body_data):
            return
        self.cursor.execute("INSERT INTO employee(first_name, last_name, address, city, state, zip)"
                            " VALUES(?,?,?,?,?,?)", (self.data['first_name'], self.data.get('last_name'),
                                                     self.data.get('address'), self.data.get('city'),
                                                     self.data.get('state'), self.data['zip']))
        logging.info("New entry created successfully with first_name ad {}".format(self.data['first_name']))
        self.db.commit()
        self.db.close()
        self.set_status(201)
        self.write("Data is inserted successfully")

    def put(self, emp_id):
        """
        method to handle the UPDATE(PUT) request from the client
        :param emp_id:
        :return:
        """
        body_data = self.request.body
        if not self.validate_data(body_data):
            return
        self.cursor.execute("UPDATE employee set first_name=?, last_name=?, address=?, city=?, state=?, zip=? "
                            " WHERE emp_id=?", (self.data['first_name'], self.data.get('last_name'),
                                                self.data.get('address'), self.data.get('city'),
                                                self.data.get('state'), self.data['zip'], int(emp_id)))
        logging.info("employee information is updated successfully with emp_id {}".format(int(emp_id)))
        self.db.commit()
        self.db.close()
        self.set_status(201)
        self.write("Data updated successfully")

    def delete(self, emp_id):
        """
        method to handle the DELETE request from the client
        :param emp_id:
        :return:
        """
        self.cursor.execute('''DELETE from employee where emp_id=?''', emp_id)
        logging.info("employee row deleted successfully with id {}".format(int(emp_id)))
        self.db.commit()
        self.db.close()
        self.set_status(200)
        self.write("Data deleted successfully")


class Application(tornado.web.Application):
    """
    Application initialization
    """
    def __init__(self):
        handlers = [
            (r"/", HomeHandler, dict(database=DATABASE_NAME)),
            (r"/api/", EmployeeHandler, dict(database=DATABASE_NAME)),
            (r"/api/([0-9]+)", EmployeeHandler, dict(database=DATABASE_NAME))
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    InitializeDatabase()
    app = Application()
    app.listen(9000)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
