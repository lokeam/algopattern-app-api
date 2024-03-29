"""
Tests for the ingredients API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Datastructure,
    Pattern,
)

from pattern.serializers import DatastructureSerializer


DS_URL = reverse('pattern:datastructure-list')


def detail_url(datastructure_id):
    """Create and return a datastructure detail URL"""
    return reverse('pattern:datastructure-detail', args=[datastructure_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test - Unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test - Require Authentication to retrieve Datastructures."""
        res = self.client.get(DS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test - Authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of datastructure."""
        Datastructure.objects.create(user=self.user, name='Array')
        Datastructure.objects.create(user=self.user, name='Heap')

        res = self.client.get(DS_URL)

        datastructures = Datastructure.objects.all().order_by('-name')
        serializer = DatastructureSerializer(datastructures, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Datastructure.objects.create(user=user2, name='LinkedList')
        datastructure = Datastructure.objects.create(
            user=self.user,
            name='DoublyLinkedList')

        res = self.client.get(DS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], datastructure.name)
        self.assertEqual(res.data[0]['id'], datastructure.id)

    def test_update_datastructure(self):
        """Test - Update a Datastructure"""
        datastructure = Datastructure.objects.create(
            user=self.user, name='HashMap')

        payload = {'name': 'Trie'}
        url = detail_url(datastructure.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        datastructure.refresh_from_db()
        self.assertEqual(datastructure.name, payload['name'])

    def test_delete_datastructure(self):
        """Test - Deleting a Datastructure"""
        datastructure = Datastructure.objects.create(
            user=self.user, name='LinkedList')

        url = detail_url(datastructure.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        datastructures = Datastructure.objects.filter(user=self.user)
        self.assertFalse(datastructures.exists())

    def test_filter_datastructures_assigned_to_patterns(self):
        """Test - List Datastructures assigned to Patterns"""
        ds1 = Datastructure.objects.create(user=self.user, name='Array')
        ds2 = Datastructure.objects.create(user=self.user, name='HashMap')
        pattern = Pattern.objects.create(
            title='FastandSlow',
            user=self.user,
        )
        pattern.datastructures.add(ds1)

        res = self.client.get(DS_URL, {'assigned_only': 1})

        s1 = DatastructureSerializer(ds1)
        s2 = DatastructureSerializer(ds2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test - Filtered datastructures returns list unique to DS"""
        ing = Datastructure.objects.create(user=self.user, name='Array')
        Datastructure.objects.create(user=self.user, name='LinkedList')
        pattern1 = Pattern.objects.create(
            title='Sliding Window',
            user=self.user,
        )
        pattern2 = Pattern.objects.create(
            title='Two Pointers',
            user=self.user,
        )
        pattern1.datastructures.add(ing)
        pattern2.datastructures.add(ing)

        res = self.client.get(DS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
