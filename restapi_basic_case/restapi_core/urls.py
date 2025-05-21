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

# Creating nested routers for Issue and comments
proj_router = NestedSimpleRouter(router, r'projects', lookup='project')
proj_router.register(r'issues', IssueViewSet, basename='issues')
cns = 'contributors'
proj_router.register(r'contributors', ContributorViewSet, basename=cns)
issue_router = NestedSimpleRouter(proj_router, r'issues', lookup='issue')
issue_router.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(proj_router.urls)),
    path('api/', include(issue_router.urls)),
]
