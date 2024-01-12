"""
URL Mappings for the Algo Pattern App
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from pattern import views


router = DefaultRouter()
router.register('patterns', views.PatternViewSet)
router.register('tags', views.TagViewSet),
router.register('datastructures', views.DatastructureViewSet)

app_name = 'pattern'

urlpatterns = [
    path('', include(router.urls)),
]
