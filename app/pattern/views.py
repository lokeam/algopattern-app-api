"""
Views for the Pattern APIs
"""
from rest_framework import (
    viewsets,
    mixins,
    status
)
from rest_framework.decorators import action
from rest_framework.response import Response
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
        elif self.action == 'upload_image':
            return serializers.PatternImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """When we perform a creation of a new obj via this viewset,
        create a new algo pattern"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to pattern."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasePatternAttrViewSet(mixins.DestroyModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """Generic Viewsets for Pattern Attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Override get_queryset method to filter down to created user"""
        return self.queryset.filter(
            user=self.request.user).order_by('-name')


class TagViewSet(BasePatternAttrViewSet):
    """Manage Tags within database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class DatastructureViewSet(BasePatternAttrViewSet):
    """Manage Datastructures in the database"""
    serializer_class = serializers.DatastructureSerializer
    queryset = Datastructure.objects.all()
