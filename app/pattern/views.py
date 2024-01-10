"""
Views for the Pattern APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Pattern
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
