import json

from tests.base import BaseTest
from api import api

class TestAPI(BaseTest):

    def setUp(self):
        super(TestAPI, self).setUp()
        self.app = api.app.test_client()


    def tearDown(self):
        super(TestAPI, self).tearDown()


    def test_health_check_returns_200(self):
        response = self.app.get("/api/v1/health-check")
        self.assertEqual(200, response.status_code)


    def test_create_user_returns_200(self):
        data = json.dumps({"username": "testuser", "password": "testpass"})
        response = self.app.post("/api/v1/create-user", data=data)
        self.assertEqual(200, response.status_code)


    def test_create_user_returns_422_with_missing_data(self):
        response = self.app.post("/api/v1/create-user")
        self.assertEqual(422, response.status_code)


    def test_create_user_returns_422_for_incorrectly_formatted_data(self):
        data = {"username": "testuser", "password": "testpass"}
        response = self.app.post("/api/v1/create-user", data=data)
        self.assertEqual(422, response.status_code)


    def test_create_user_returns_422_if_missing_username_or_password(self):
        data = json.dumps({"username": "testuser"})
        response = self.app.post("/api/v1/create-user", data=data)
        self.assertEqual(422, response.status_code)

        data = json.dumps({"password": "testpass"})
        response = self.app.post("/api/v1/create-user", data=data)
        self.assertEqual(422, response.status_code)


    def test_create_user_returns_422_if_username_or_password_are_empty(self):
        data = json.dumps({"username": "testuser", "password": ""})
        response = self.app.post("/api/v1/create-user", data=data)
        self.assertEqual(422, response.status_code)

        data = json.dumps({"username": "", "password": "testpass"})
        response = self.app.post("/api/v1/create-user", data=data)
        self.assertEqual(422, response.status_code)


    def test_create_user_saves_new_user_to_db(self):
        data = json.dumps({"username": "testuser", "password": "testpass"})
        self.app.post("/api/v1/create-user", data=data)

        query = "SELECT COUNT(*) FROM users"
        curr = self.conn.cursor()
        curr.execute(query)
        results = curr.fetchall()
        self.assertEqual(1, results[0][0])


    def test_create_user_creates_user_with_correct_username(self):
        username = "testuser"
        password = "testpass"

        data = json.dumps({"username": username, "password": password})
        self.app.post("/api/v1/create-user", data=data)

        query = "SELECT username, password FROM users"
        curr = self.conn.cursor()
        curr.execute(query)
        results = curr.fetchall()
        self.assertEqual(username, results[0][0])


    def test_create_user_creates_user_with_correct_first_and_last_name(self):
        username = "testuser"
        password = "testpass"
        first_name = "First"
        last_name = "Last"

        data = json.dumps({
            "username": username, 
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        })
        result = self.app.post("/api/v1/create-user", data=data)

        query = "SELECT first_name, last_name FROM users"
        curr = self.conn.cursor()
        curr.execute(query)
        results = curr.fetchall()
        self.assertEqual(first_name, results[0][0])
        self.assertEqual(last_name, results[0][1])


    def test_create_user_creates_user_as_student_by_default(self):
        username = "testuser"
        password = "testpass"

        data = json.dumps({"username": username, "password": password})
        self.app.post("/api/v1/create-user", data=data)

        query = "SELECT user_type FROM users"
        curr = self.conn.cursor()
        curr.execute(query)
        results = curr.fetchall()
        self.assertEqual("student", results[0][0])

