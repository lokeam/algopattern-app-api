"""
Serializers for Pattern APIs
"""
from rest_framework import serializers

from core.models import (
    Pattern,
    Tag
)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class PatternSerializer(serializers.ModelSerializer):
    """Serializer for Patterns"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Pattern
        fields = ['id', 'title', 'link', 'tags']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a Pattern"""
        tags = validated_data.pop('tags', [])
        pattern = Pattern.objects.create(**validated_data)
        auth_user = self.context['request'].user

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            pattern.tags.add(tag_obj)

        return pattern


class PatternDetailSerializer(PatternSerializer):
    """Serializer for the pattern detail view"""

    class Meta(PatternSerializer.Meta):
        fields = PatternSerializer.Meta.fields + ['description']
