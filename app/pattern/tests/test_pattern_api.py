"""
Tests for Pattern APIs
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Pattern,
    Tag
)

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


def create_user(**params):
    """Create a return a new User"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
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

    def test_create_pattern(self):
        """Test - Create a Algo Pattern via API"""
        payload = {
            'title': 'Sample algo pattern',
            'link': 'http://example.com/sliding-window.pdf'
        }
        res = self.client.post(PATTERN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pattern = Pattern.objects.get(id=res.data['id'])

        for key, value in payload.items():
            self.assertEqual(getattr(pattern, key), value)
        self.assertEqual(pattern.user, self.user)

    def test_partial_update(self):
        """Test - Partially update a Pattern"""
        original_link = 'https://example.com/pattern.pdf'
        pattern = create_pattern(
            user=self.user,
            title='Sample pattern title',
            link=original_link,
        )

        payload = {'title': 'New pattern title'}
        url = detail_url(pattern.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        pattern.refresh_from_db()
        self.assertEqual(pattern.title, payload['title'])
        self.assertEqual(pattern.user, self.user)

    def test_create_pattern_with_new_tags(self):
        """Test - Creating a Pattern with New Tags"""
        payload = {
            'title': 'Unique sort',
            'tags': [{'name': 'HashMap'}, {'name': 'Sort'}]
        }
        res = self.client.post(PATTERN_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        patterns = Pattern.objects.filter(user=self.user)
        self.assertEqual(patterns.count(), 1)
        pattern = patterns[0]
        self.assertEqual(pattern.tags.count(), 2)

        for tag in payload['tags']:
            exists = pattern.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_pattern_with_existing_tags(self):
        """Test - Create a recipe with existing tag"""
        tag_string = Tag.objects.create(user=self.user, name='String')
        payload = {
            'title': 'Sliding Window',
            'tags': [{'name': 'String'}, {'name': 'Array'}],
        }
        res = self.client.post(PATTERN_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        patterns = Pattern.objects.filter(user=self.user)
        self.assertEqual(patterns.count(), 1)
        pattern = patterns[0]
        self.assertEqual(pattern.tags.count(), 2)
        self.assertIn(tag_string, pattern.tags.all())

        for tag in payload['tags']:
            exists = pattern.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test - Create tag when updating a Pattern."""
        recipe = create_pattern(user=self.user)

        payload = {'tags': [{'name': 'Array'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Array')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='String')
        recipe = create_pattern(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_arr = Tag.objects.create(user=self.user, name='Array')
        payload = {'tags': [{'name': 'Array'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_arr, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags."""
        tag = Tag.objects.create(user=self.user, name='BFS')
        recipe = create_pattern(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)