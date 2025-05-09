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

        if request.method in ("DELETE", "PATCH"):
            if request.user.is_superuser:
                return True

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
        if request.method in SAFE_METHODS:
            if not request.user.is_superuser:
                return request.user in obj.project.contributors.all()

            return True

        if request.method in ("DELETE", "PATCH"):
            if not request.user.is_superuser:
                return Contributor.objects.filter(
                    project=obj.project,
                    user=request.user,
                    role='A').exists()

            return True


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
        if request.method in ("PATCH", "DELETE"):
            if request.user == obj.author:
                return True
            return False
        return obj.author == request.user


class CommentPermission(BasePermission):
    """
    Custom permission class to check if the user is the owner of the project.
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            serializer = view.get_serializer(data=request.data)
            if not serializer.is_valid():
                return False
            data = serializer.validated_data
            issue = data.get('issue')
            if request.user not in issue.contributors.all():
                return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if not request.user.is_superuser:
                return request.user in obj.issue.contributors.all()
            return True
        if request.method == "DELETE":
            if request.user == obj.author:
                return True
            return False
        return obj.author == request.user
