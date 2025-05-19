from django.urls import path, include
from restapi_core.views import (CustomUserViewSet, ProjectViewSet,
                                ContributorViewSet, IssueViewSet,
                                CommentViewSet, LoginViewSet, LogoutViewSet)
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter


router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'logout', LogoutViewSet, basename='logout')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'contributors', ContributorViewSet, basename='contributors')

# Creating nested routers for Issue and comments
project_router = NestedSimpleRouter(router, r'projects', lookup='project')
project_router.register(r'issues', IssueViewSet, basename='issues')

issue_router = NestedSimpleRouter(project_router, r'issues', lookup='issue')
issue_router.register(r'comments', CommentViewSet, basename='comments')

# router.register(r'issues', IssueViewSet, basename='issues')
# router.register(r'comments', CommentViewSet, basename='comments')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(project_router.urls)),
    path('api/', include(issue_router.urls)),
]
