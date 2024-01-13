"""
Tests for Pattern APIs
"""
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Pattern,
    Tag,
    Datastructure,
)

from pattern.serializers import (
    PatternSerializer,
    PatternDetailSerializer,
)


PATTERN_URL = reverse('pattern:pattern-list')


def detail_url(pattern_id):
    """Create and return a pattern detail URL"""
    return reverse('pattern:pattern-detail', args=[pattern_id])


def image_upload_url(recipe_id):
    """Create and return an image upload URL."""
    return reverse('pattern:pattern-upload-image', args=[recipe_id])


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
        """Test - Create a Pattern with existing tag"""
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
        """Test - Create tag when updating a Pattern"""
        pattern = create_pattern(user=self.user)

        payload = {'tags': [{'name': 'Array'}]}
        url = detail_url(pattern.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Array')
        self.assertIn(new_tag, pattern.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test - Assign existing tag when updating a Pattern"""
        tag_string = Tag.objects.create(user=self.user, name='String')
        pattern = create_pattern(user=self.user)
        pattern.tags.add(tag_string)

        tag_arr = Tag.objects.create(user=self.user, name='Array')
        payload = {'tags': [{'name': 'Array'}]}
        url = detail_url(pattern.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_arr, pattern.tags.all())
        self.assertNotIn(tag_string, pattern.tags.all())

    def test_clear_pattern_tags(self):
        """Test - Delete a Pattern's Tags"""
        tag = Tag.objects.create(user=self.user, name='BFS')
        pattern = create_pattern(user=self.user)
        pattern.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(pattern.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(pattern.tags.count(), 0)

    def test_create_pattern_with_new_datastructures(self):
        """Test - Create a Pattern with new Datastructures"""
        payload = {
            'title': 'Two Pointer',
            'datastructures': [{'name': 'Array'}, {'name': 'Vector'}],
        }
        res = self.client.post(PATTERN_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        patterns = Pattern.objects.filter(user=self.user)
        self.assertEqual(patterns.count(), 1)
        pattern = patterns[0]
        self.assertEqual(pattern.datastructures.count(), 2)
        for ingredient in payload['datastructures']:
            exists = pattern.datastructures.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_pattern_with_existing_datastructure(self):
        """Test - Create a new pattern with existing Datastructures"""
        datastructure = Datastructure.objects.create(
            user=self.user, name='Trie')
        payload = {
            'title': 'Breadth First Search',
            'time_minutes': 25,
            'price': '2.55',
            'datastructures': [{'name': 'Trie'}, {'name': 'Graph'}],
        }
        res = self.client.post(PATTERN_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        patterns = Pattern.objects.filter(user=self.user)
        self.assertEqual(patterns.count(), 1)
        pattern = patterns[0]
        self.assertEqual(pattern.datastructures.count(), 2)
        self.assertIn(datastructure, pattern.datastructures.all())

        for datastructure in payload['datastructures']:
            exists = pattern.datastructures.filter(
                name=datastructure['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_datastructure_on_update(self):
        """Test - Ceating datastructure when updating a Pattern"""
        pattern = create_pattern(user=self.user)

        payload = {'datastructures': [{'name': 'Array'}]}
        url = detail_url(pattern.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_datastructure = Datastructure.objects.get(
            user=self.user, name='Array')
        self.assertIn(new_datastructure, pattern.datastructures.all())

    def test_update_pattern_assign_datastructure(self):
        """Test - Assign existing datastructure during Pattern update"""
        ds1 = Datastructure.objects.create(user=self.user, name='Array')
        pattern = create_pattern(user=self.user)
        pattern.datastructures.add(ds1)

        ds2 = Datastructure.objects.create(user=self.user, name='HashMap')
        payload = {'datastructures': [{'name': 'HashMap'}]}
        url = detail_url(pattern.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ds2, pattern.datastructures.all())
        self.assertNotIn(ds1, pattern.datastructures.all())

    def test_clear_pattern_datastructures(self):
        """Test - Wipe a pattern's listed datastructures"""
        datastructure = Datastructure.objects.create(
            user=self.user, name='LinkedList')
        pattern = create_pattern(user=self.user)
        pattern.datastructures.add(datastructure)

        payload = {'datastructures': []}
        url = detail_url(pattern.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(pattern.datastructures.count(), 0)

    def test_filter_by_tags(self):
        """Test - Filter Patterns by Associated Tags"""
        r1 = create_pattern(user=self.user, title='Two Pointer')
        r2 = create_pattern(user=self.user, title='Topological sort')
        tag1 = Tag.objects.create(user=self.user, name='Array')
        tag2 = Tag.objects.create(user=self.user, name='HashMap')
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_pattern(user=self.user, title='Merge Intervals')

        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(PATTERN_URL, params)

        s1 = PatternSerializer(r1)
        s2 = PatternSerializer(r2)
        s3 = PatternSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_datastructures(self):
        """Test - Filter Patterns by Data Structures"""
        r1 = create_pattern(user=self.user, title='Sliding Window')
        r2 = create_pattern(user=self.user,
                            title='In-place Linked List Reversal')
        in1 = Datastructure.objects.create(user=self.user, name='Array')
        in2 = Datastructure.objects.create(user=self.user, name='LinkedList')
        r1.datastructures.add(in1)
        r2.datastructures.add(in2)
        r3 = create_pattern(user=self.user, title='Tree DFS')

        params = {'datastructures': f'{in1.id},{in2.id}'}
        res = self.client.get(PATTERN_URL, params)

        s1 = PatternSerializer(r1)
        s2 = PatternSerializer(r2)
        s3 = PatternSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTests(TestCase):
    """Tests for the Image Upload API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_pattern(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a pattern."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
