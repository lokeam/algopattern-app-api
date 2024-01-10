"""
Serializers for Pattern APIs
"""
from rest_framework import serializers

from core.models import Pattern


class PatternSerializer(serializers.ModelSerializer):
    """Serializer for Patterns"""

    class Meta:
        model = Pattern
        fields = ['id', 'title', 'link']
        read_only_fields = ['id']
