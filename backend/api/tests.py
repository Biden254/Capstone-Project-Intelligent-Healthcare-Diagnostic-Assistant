from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class HealthEndpointTests(TestCase):
    def test_health_is_public_and_ok(self):
        client = APIClient()
        response = client.get(reverse('health'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')


class AuthFlowTests(TestCase):
    def test_register_then_access_protected_endpoint(self):
        client = APIClient()

        register_response = client.post(reverse('auth-register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
        }, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        access_token = register_response.data['access']

        # No token -> should be rejected
        me_response = client.get(reverse('auth-me'))
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # With token -> should succeed
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        me_response = client.get(reverse('auth-me'))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['username'], 'testuser')
