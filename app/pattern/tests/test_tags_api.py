"""
Tests for Tags API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Pattern,
)

from pattern.serializers import TagSerializer

TAGS_URL = reverse('pattern:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail URL"""
    return reverse('pattern:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a User"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicPatternAPITests(TestCase):
    """Test - Unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePatternApiTests(TestCase):
    """Test - Authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Array')
        Tag.objects.create(user=self.user, name='String')
        Tag.objects.create(user=self.user, name='Two Pointers')
        Tag.objects.create(user=self.user, name='Sliding Window')
        Tag.objects.create(user=self.user, name='Recursion')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test - Listed Tags limited to authenticated User"""
        user2 = create_user(email='user5@example.com')
        Tag.objects.create(user=user2, name='Stack')
        tag = Tag.objects.create(user=self.user, name='Sorting')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name='Breadth First Search')

        payload = {'name': 'BFS'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test - Deleting a Tag"""
        tag = Tag.objects.create(user=self.user, name='BFS')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test - Display Tags assigned to Patterns"""
        tag1 = Tag.objects.create(user=self.user, name='PriorityQueue')
        tag2 = Tag.objects.create(user=self.user, name='Scheduling')
        pattern = Pattern.objects.create(
            title='TwoHeaps',
            user=self.user,
        )
        pattern.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test - Filtered Tags returns list unique to Tags"""
        tag = Tag.objects.create(user=self.user, name='Array')
        Tag.objects.create(user=self.user, name='LinkedList')
        pattern1 = Pattern.objects.create(
            title='TwoPointers',
            user=self.user,
        )
        pattern2 = Pattern.objects.create(
            title='FastandSlow',
            user=self.user,
        )
        pattern1.tags.add(tag)
        pattern2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
