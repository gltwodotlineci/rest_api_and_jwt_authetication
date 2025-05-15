from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Contributor


class ProjectPermission(BasePermission):
    """
    Custom permission class to check if the user is the owner of the project.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return obj.project_contributors.filter(
                user=request.user).exists()

        return obj.project_contributors.filter(
            role="A", user=request.user).exists()


class ContributorPermission(BasePermission):
    """
    Custom permission class to check if the user is the owner of the project.
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            if request.user.is_superuser:
                return True
            serializer = view.get_serializer(data=request.data)
            if not serializer.is_valid():
                return False
            data = serializer.validated_data
            project = data.get('project')
            contributors = project.contributors.all()
            if request.user not in contributors:
                return False

            return project.project_contributors.all().filter(
                user=request.user, role="A").exists()

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return request.user in obj.project.contributors.all()

        if request.method == "DELETE":
            if not request.user.is_superuser:
                return Contributor.objects.filter(
                    project=obj.project,
                    user=request.user,
                    role='A').exists()

            return True


class IssueCommentAuthor(BasePermission):
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
            if project is None:
                project = data.get("issue").project

            if request.user not in project.contributors.all():
                return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return request.user in obj.project.contributors.all()

        if request.method in ("PATCH", "DELETE"):
            return obj.author == request.user
