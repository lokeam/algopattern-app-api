"""
Tests for Models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test - successfully creating a user with an email"""
        email = "testyTest@example.com"
        password = "testpassword987"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test - Create list of user emails, ensure all normalized"""
        sample_emails = [
            ['test1@ExAmple.com', 'test1@example.com'],
            ['Test2@examplE.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_throws_error(self):
        """Test - Ensure that each users has an associated email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test - Creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'superTest@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
