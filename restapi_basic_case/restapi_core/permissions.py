from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Contributor


class IsContributorOrAuthor(BasePermission):
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
            return Contributor.objects.filter(
                user=request.user,
                project=obj.issue
            ).exists()
        # Allow other methods to proceed to object-level permission check
        return obj.author == request.user
