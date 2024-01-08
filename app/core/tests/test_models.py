"""
Tests for Models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):


    """Test - successfully creating a user with an email"""
    def test_create_user_with_email_successful(self):
        email = "testyTest@example.com"
        password = "testpassword987"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
