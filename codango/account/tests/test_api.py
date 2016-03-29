from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User

# DRY variables to be used repeatedly
user = {'username': 'stanmd', 'email': 'ndagi@gmail.com', 'password': '1234'}
message = {"detail":
           "Authentication credentials were not provided."}

url = '/api/v1/users/'
url_for_one = '/api/v1/users/4'
url_for_one_follow = '/api/v1/users/4/follow/'
url_for_one_settings = '/api/v1/users/4/settings/'
not_found_msg = {"detail": "Not found."}


class UserTests(APITestCase):

    # Include two users for testing purposes
    fixtures = ['users.json']

    def setUp(self):
        # Login the user
        auth_user = {'username': 'stan',
                     'password': '1234'}
        login_response = self.client.post('/api/v1/auth/login/', auth_user)
        self.token = 'JWT ' + login_response.data.get('token')

    def test_create_user(self):
        """
        Ensure we can create a new user object.
        """
        response = self.client.post('/api/v1/auth/register/',
                                    user, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 5)
        self.assertEqual(User.objects.filter(username='stanmd').first().email, 'ndagi@gmail.com')

    def test_login(self):
        """Ensure we can login"""
        # create user
        self.client.post('/api/v1/auth/register/', user, format='json')
        # attempt login
        auth_user = {'username': 'stanmd',
                     'password': user['password']}

        # Login first to get token
        login_response = self.client.post('/api/v1/auth/login/', auth_user)
        self.assertTrue('token' in login_response.data)
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.status_text, 'OK')
        self.assertNotEqual(login_response.data.get('token'), None)

    def test_retrieve_users(self):
        """ONLY ADMIN: Test Retrieve users"""
        # Test FALSE access w/out authentication
        plain_response = self.client.get(url)
        self.assertEqual(plain_response.data, message)
        self.assertNotEqual(plain_response.data, {})
        self.assertEqual(plain_response.status_code, 401)

        # set authentication token in header
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        # Asserting TRUE access
        auth_response = self.client.get(url)
        self.assertEqual(auth_response.data['count'], 4)
        self.assertEqual(auth_response.data['results'][0]['id'], True)
        self.assertEqual(auth_response.status_code, 200)
        self.assertNotEqual(auth_response.data, {})

    def test_pagination_users(self):
        """Test pagination."""
        # set authentication token in header
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        auth_response = self.client.get(url)

        # Assert pagination The number is specified in the settings/base.py
        self.assertEqual(auth_response.data['next'],
                         "http://testserver/api/v1/users/?page=2")
        # Null in JSON is equal to None in Python
        self.assertEqual(auth_response.data['previous'], None)
        self.assertEqual(len(auth_response.data['results']), 3)
        self.assertEqual(auth_response.status_code, 200)
        self.assertNotEqual(auth_response.data, {})
        next_page_url = '/api/v1/users/?page=2'
        self.assertEqual(self.client.get(next_page_url).data['next'],
                         None)
        self.assertEqual(self.client.get(next_page_url).data['previous'],
                         "http://testserver/api/v1/users/")
        self.assertEqual(len(auth_response.data['results']), 3)

    def test_retrieve_specific_user(self):
        """Test Retrieve specific user."""
        # Test FALSE access w/out authentication
        plain_response = self.client.get(url_for_one)
        self.assertEqual(plain_response.data, message)
        self.assertNotEqual(plain_response.data, {})
        self.assertEqual(plain_response.status_code, 401)

        # set authentication token in header
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # Get to the specific resources url
        auth_response = self.client.get(url_for_one)

        # Asserting TRUE access and retrieval of one resource
        self.assertNotEqual(auth_response.data, not_found_msg)
        self.assertEqual(auth_response.status_code, 200)
        self.assertEqual(auth_response.data.get('id'), None)
        self.assertEqual(auth_response.data.get('username'), 'achile')

    def test_update_specific_user(self):
        """Test Update specific user."""
        update_info = {"username": "aegbunu", "email": "ndagis@gmail.com", "userprofile": {"first_name": "Achile"}}

        # Test FALSE access w/out authentication
        plain_response = self.client.put(url_for_one, update_info)
        self.assertEqual(plain_response.data, message)
        self.assertNotEqual(plain_response.data, {})
        self.assertEqual(plain_response.status_code, 401)

        # set authentication token in header
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # Update at the specific resources url
        auth_response = self.client.put(url_for_one, update_info)
        # Asserting TRUE access and update of specified resource
        self.assertEqual(auth_response.status_code, 200)
        self.assertNotEqual(auth_response.data.get('username'), 'achile')
        self.assertEqual(auth_response.data.get('username'), 'aegbunu')

    def test_retrieve_specific_user_settings(self):
        """Test Retrieve specific user settings."""

        # Test FALSE access w/out authentication
        plain_response = self.client.get(url_for_one)
        self.assertEqual(plain_response.data, message)
        self.assertNotEqual(plain_response.data, {})
        self.assertEqual(plain_response.status_code, 401)

        # set authentication token in header
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # Update at the specific resources url
        auth_response = self.client.get(url_for_one)

        # Asserting TRUE access and update of specified resource
        self.assertEqual(auth_response.status_code, 200)
        self.assertEqual(auth_response.data.get('username'), 'achile')
        # self.assertEqual(auth_response.data.get('userprofile.place_of_work'), 'Andela')
        # self.assertNotEqual(auth_response.data.get('userprofile.place_of_work'), 'Andela Nigeria')
        # self.assertEqual(auth_response.data.get('languages.name'), 'PYTHON')

    def test_update_specific_user_settings(self):
        """Test Update specific user settings."""
        update_info = {"username": "aegbunu", "email": "ndagis@gmail.com",
                       "password": "some password",
                       "userprofile": {
                            "place_of_work": "Andela Nigeria",
                            "position": "Class Three Nairobi Kenya",
                            "about": "Jovial guy",
                            "github_username": 'Achile',
                            "frequency": "daily"
                        },
                        "languages": {
                            "name": 'JAVASCRIPT'
                        }}

        # Test FALSE access w/out authentication
        plain_response = self.client.put(url_for_one, update_info)
        self.assertEqual(plain_response.data, message)
        self.assertNotEqual(plain_response.data, {})
        self.assertEqual(plain_response.status_code, 401)

        # set authentication token in header
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # Update at the specific resources url
        auth_response = self.client.put(url_for_one, update_info)

        # Asserting TRUE access and update of specified resource
        self.assertEqual(auth_response.status_code, 200)
        self.assertNotEqual(auth_response.data.get('username'), 'achile')
        # self.assertNotEqual(auth_response.data.get('userprofile.place_of_work'), 'Andela')
        # self.assertEqual(auth_response.data.get('userprofile.place_of_work'), 'Andela Nigeria')
        # self.assertEqual(auth_response.data.get('languages.name'), 'JAVASCRIPT')

        """
        Will be included in the CRUD of endpoints upon authentication

        TO TEST AUTH PER URL
        token = 'JWT ' + login_response.data.get('token')
        # set authentication token in header
        self.client.credentials(HTTP_AUTHORIZATION=token)
        auth_response = self.client.post('/api/v1/....')
        """
