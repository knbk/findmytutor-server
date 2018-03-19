from django.urls import reverse

from rest_framework.test import APITestCase


class AccountsTestCase(APITestCase):
    def test_root_api_view(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

    def test_list_accounts(self):
        response = self.client.get(reverse('student-list'))
        self.assertEqual(response.status_code, 200)

    def test_list_users(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)
