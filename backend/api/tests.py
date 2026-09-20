from django.test import TestCase
from rest_framework.test import APIClient


class HealthCheckTest(TestCase):
    """Smoke test: verify the health-check endpoint responds."""

    def test_health_check_returns_ok(self):
        client = APIClient()
        response = client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['project'], 'Joyory SmartMatch')
