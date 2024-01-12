"""
Views for the Pattern APIs
"""
from rest_framework import (
    viewsets,
    mixins
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Pattern,
    Tag,
    Datastructure,
)
from pattern import serializers


class PatternViewSet(viewsets.ModelViewSet):
    """View for manage Pattern APIs"""
    serializer_class = serializers.PatternSerializer
    queryset = Pattern.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipies for authenticated User"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'retrieve':
            return serializers.PatternDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """When we perform a creation of a new obj via this viewset,
        create a new algo pattern"""
        serializer.save(user=self.request.user)


class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Manage Tags within database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Override get_queryset method to filter down to created user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class DatastructureViewSet(mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    """Manage Datastructures in the database"""
    serializer_class = serializers.DatastructureSerializer
    queryset = Datastructure.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
