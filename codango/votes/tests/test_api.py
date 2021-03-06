from rest_framework import status
from rest_framework.test import APITestCase

message = {"detail":
           "Authentication credentials were not provided."}


class VoteTest(APITestCase):
    """Test /api/v1/votes/ endpoint"""
    def test_vote(self):
        response = self.client.get('/api/v1/votes/')
        self.assertEqual(response.data, message)
        self.assertNotEqual(response.data, {})
        self.assertEqual(response.status_code, 401)

    """
    Will be included in the CRUD of endpoints upon authentication

    TO TEST AUTH PER URL
    token = 'JWT ' + login_response.data.get('token')
    # set authentication token in header
    self.client.credentials(HTTP_AUTHORIZATION=token)
    auth_response = self.client.post('/api/v1/....')
    """
