# RestApiWithTornado
Curd Operations with Tornado Web Server and SqLite3

Steps for project setup

step1 : git clone git@github.com:ramchauhan/RestApiWithTornado.git
step2 : cd RestApiWithTornado
Step2 : pip install -r requirement.txt
step4 : python app/service.py 

Note: This will Application will generate emp_id dynamically. Here first_name and zip are mandatory fields
You can insert the data by using rest service or by using form


Now you can perform below task

1: You can View all information in Browser
   Since server is running at 9000 port so use http://localhost:9000/

2: You can perform CRUD opration by using any rest client like postman or by using "curl"

FOR GET: 

URL: http://localhost:9000/api/<emp_id>
Sample out put:

""
[
    {
        "city": "Azamgarh",
        "first_name": "ram",
        "last_name": "Chauhan",
        "zip": 123456,
        "state": "Uttar Pradesh",
        "address": "xyz",
        "id": 3
    }
]
""

FOR POST:
URL: http://localhost:9000/api/
Sample raw data

{"city": "Azamgarh", "first_name": "Ashok", "last_name": "Chauhan", "zip": 123456, "state": "Uttar Pradesh", "address": "xyz"}


FOR PUT:
URL: http://localhost:9000/api/
Sample raw data

{"city": "Azamgarh", "first_name": "Ashok", "last_name": "Chauhan", "zip": 123456, "state": "Uttar Pradesh", "address": "xyz"}


FOR DELETE:
URL: http://localhost:9000/api/<emp_id>






