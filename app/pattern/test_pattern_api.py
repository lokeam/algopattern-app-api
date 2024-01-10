"""
Tests for Pattern APIs
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Pattern

from pattern.serializers import (
    PatternSerializer,
    PatternDetailSerializer,
)


PATTERN_URL = reverse('pattern:pattern-list')


def detail_url(pattern_id):
    """Create and return a pattern detail URL"""
    return reverse('pattern:pattern-detail', args=[pattern_id])


def create_pattern(user, **params):
    """Create and return a sample algo pattern"""
    defaults = {
        'title': 'Sample pattern title',
        'link': 'http://example.com/pattern.pdf',
    }
    defaults.update(params)

    pattern = Pattern.objects.create(user=user, **defaults)
    return pattern


class PublicPatternAPITests(TestCase):
    """Test - Unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test - Require authentication to call API"""
        res = self.client.get(PATTERN_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePatternApiTests(TestCase):
    """Test - Authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test - Render a list of algo patterns specific to User Account"""
        create_pattern(user=self.user)
        create_pattern(user=self.user)

        res = self.client.get(PATTERN_URL)

        patterns = Pattern.objects.all().order_by('-id')
        serializer = PatternSerializer(patterns, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_pattern_detail(self):
        """Test - Get Specific Details of an Algo Pattern"""
        pattern = create_pattern(user=self.user)

        url = detail_url(pattern.id)
        res = self.client.get(url)

        serializer = PatternDetailSerializer(pattern)
        self.assertEqual(res.data, serializer.data)
