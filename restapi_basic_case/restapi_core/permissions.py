from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Contributor, Project


class UserPermission(BasePermission):
    """
    Custom permission class to check if the user is authenticated
    And check his profile, or all profiles if he's admin
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            if not request.user.is_superuser:
                return False
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return obj == request.user
        if request.method == "DELETE":
            if request.user.is_superuser:
                return True
            return False


class ProjectPermission(BasePermission):
    """
    Custom permission class to check if the user is the owner of the project.
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            if request.user.is_superuser:
                return True

        return True

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

            proj_id = request.data.get('project')
            project = Project.objects.get(uuid=proj_id)

            return project.project_contributors.all().filter(
                user=request.user, role="A").exists()

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return obj.project.contributors.filter(
                user=request.user).exists()

        if request.method == "DELETE":
            return Contributor.objects.filter(
                project=obj.project,
                user=request.user,
                role='A').exists()


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

            return project.contributors.filter(
                uuid=request.user.pk).exists()

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return request.user in obj.project.contributors.all()

        if request.method in ("PATCH", "DELETE", "PUT"):
            return obj.author == request.user
