from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Contributor


class ProjectPermission(BasePermission):
    """
    Custom permission class to check if the user is the owner of the project.
    """
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if not request.user.is_superuser:
                return request.user in obj.contributors.all()
            return True

            # return obj.owner == request.user

        if request.method in ("DELETE", "PATCH"):
            if request.user.is_superuser:
                return True

            return obj.project_contributors.filter(
                role="A", user=request.user).exists()


class IssueContributorOrAuthor(BasePermission):
    """
    Custom permission class to check if the user is the owner of the project.
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            serializer = view.get_serializer(data=request.data)
            if not serializer.is_valid():
                return False
            data = serializer.validated_data
            project = data.get('project')
            if request.user not in project.contributors.all():
                return False

        return True

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            if not request.user.is_superuser:
                return request.user in obj.project.contributors.all()
            return True
        if request.method == "DELETE":
            if request.user == obj.author:
                return True
            return False
        return obj.author == request.user
