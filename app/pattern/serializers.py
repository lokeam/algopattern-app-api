"""
Serializers for Pattern APIs
"""
from rest_framework import serializers

from core.models import (
    Pattern,
    Tag,
    Datastructure,
)


class DatastructureSerializer(serializers.ModelSerializer):
    """Serializer for datastructures."""

    class Meta:
        model = Datastructure
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class PatternSerializer(serializers.ModelSerializer):
    """Serializer for Patterns"""
    tags = TagSerializer(many=True, required=False)
    datastructures = DatastructureSerializer(many=True, required=False)

    class Meta:
        model = Pattern
        fields = ['id', 'title', 'link', 'tags', 'datastructures']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, pattern):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            pattern.tags.add(tag_obj)

    def _get_or_create_datastructures(self, datastructures, pattern):
        """Handle getting or creating datastructures as needed"""
        auth_user = self.context['request'].user
        for datastructure in datastructures:
            datastructure_obj, created = Datastructure.objects.get_or_create(
                user=auth_user,
                **datastructure,
            )
            pattern.datastructures.add(datastructure_obj)

    def create(self, validated_data):
        """Create a Pattern"""
        tags = validated_data.pop('tags', [])
        datastructures = validated_data.pop('datastructures', [])
        pattern = Pattern.objects.create(**validated_data)
        self._get_or_create_tags(tags, pattern)
        self._get_or_create_datastructures(datastructures, pattern)

        return pattern

    def update(self, instance, validated_data):
        """Update Pattern"""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PatternDetailSerializer(PatternSerializer):
    """Serializer for the pattern detail view"""

    class Meta(PatternSerializer.Meta):
        fields = PatternSerializer.Meta.fields + ['description']
