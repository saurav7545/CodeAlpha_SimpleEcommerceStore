from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    def test_registration_login_logout_and_protected_profile(self):
        profile_url = reverse('accounts:profile')
        self.assertRedirects(self.client.get(profile_url), f"{reverse('accounts:login')}?next={profile_url}")
        response = self.client.post(reverse('accounts:register'), {
            'first_name': 'Asha', 'last_name': 'Kumar', 'username': 'asha',
            'email': 'asha@example.com', 'password1': 'StrongPass123!', 'password2': 'StrongPass123!',
        })
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertTrue(User.objects.filter(username='asha').exists())
        response = self.client.post(reverse('accounts:login'), {'username': 'asha', 'password': 'StrongPass123!'})
        self.assertRedirects(response, reverse('products:home'))
        self.assertEqual(self.client.post(reverse('accounts:logout')).status_code, 302)
