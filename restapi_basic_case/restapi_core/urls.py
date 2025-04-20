from django.urls import path, include
from . import views
from restapi_core.views import(CustomUserViewSet, ProjectViewSet,
                               ContributorViewSet, IssueViewSet,
                               CommentViewSet)
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'contributors', ContributorViewSet, basename='contributors')
router.register(r'issues', IssueViewSet, basename='issues')
router.register(r'comments', CommentViewSet, basename='comments')


urlpatterns = [
    path('api/', include(router.urls))
]
