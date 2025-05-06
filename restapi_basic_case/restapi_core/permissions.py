from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Contributor


class IssuePermission(BasePermission):
    """
    Custom permission class to check if the user is the owner of the project.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return Contributor.objects.filter(
                user=request.user,
                project=obj.project
            ).exists()

        return obj.author == request.user
