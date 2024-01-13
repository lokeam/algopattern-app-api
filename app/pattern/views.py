"""
Views for the Pattern APIs
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('tags', OpenApiTypes.STR),
            OpenApiParameter('ingredients', OpenApiTypes.STR),
        ]
    )
)
class PatternViewSet(viewsets.ModelViewSet):
    """View for manage Pattern APIs"""
    serializer_class = serializers.PatternSerializer
    queryset = Pattern.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipies for authenticated User"""
        tags = self.request.query_params.get('tags')
        datastructures = self.request.query_params.get('datastructures')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if datastructures:
            datastructure_ids = self._params_to_ints(datastructures)
            queryset = queryset.filter(
                datastructures__id__in=datastructure_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to patterns',
            ),
        ]
    )
)
class BasePatternAttrViewSet(mixins.DestroyModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """Generic Viewsets for Pattern Attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Override get_queryset method to filter down to created user"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(pattern__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TagViewSet(BasePatternAttrViewSet):
    """Manage Tags within database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class DatastructureViewSet(BasePatternAttrViewSet):
    """Manage Datastructures in the database"""
    serializer_class = serializers.DatastructureSerializer
    queryset = Datastructure.objects.all()
