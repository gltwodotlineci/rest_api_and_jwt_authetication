from datetime import datetime, timezone, timedelta
from django.shortcuts import get_object_or_404
import jwt
# from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import CustomUser, Project, Contributor, Issue, Comment
from .serializers import CustomUserSerializer, ProjectSerializer, \
    ContributorSerializer, IssueUserSerializer, CommentSerializer
from rest_framework.exceptions import AuthenticationFailed
from .authentication import CustomJWTAuthentication
from .permissions import IssueCommentAuthor, ProjectPermission, \
    ContributorPermission, UserPermission


class CustomUserViewSet(viewsets.ViewSet):
    authentication_classes = [CustomJWTAuthentication]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated(), UserPermission()]

    def list(self, request):
        queryset = CustomUser.objects.all()
        obj_serialized = CustomUserSerializer(queryset, many=True)
        users = obj_serialized.data

        if not request.user.is_staff:
            users = [us for us in users if
                     us["username"] == request.user.username]
        return Response(users)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user)
        if request.user == user or request.user.is_staff:
            return Response(serializer.data)
        message = "You have not the right to acces to this user's data"
        return Response({False: message})

    def create(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        user = get_object_or_404(CustomUser, pk=pk)
        name_user = user.username
        if request.user.is_staff:
            user.delete()
            return Response(f"You have deletet {name_user} user")
        message = "Only the admin can delete a user"
        return Response({False: message})


class LoginViewSet(viewsets.ViewSet):
    """
    Viewset for user login.
    Verify the authentication of the user.
    """
    def create(self, request):
        """
        Verify the authentication of the user.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = CustomUser.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('Invalid credentials')
        if not user.check_password(password):
            raise AuthenticationFailed('Invalid credentials')

        payload = {
            "id": str(user.pk),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=50),
            "iat": datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        return Response({'jwt_token': token}, status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ViewSet):
    """
    Viewset for user logout.
    """
    def create(self, request):
        """
        Logout the user.
        """
        resp = Response()
        resp.delete_cookie('jwt')
        resp.data = {'message': 'signed out'}
        return resp


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Project model.
    check authentication for the user.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, ProjectPermission]
    queryset = Project.objects.all()

    serializer_class = ProjectSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']

    def get_queryset(self):
        """
        Get the list of projects.
        If the user is not staff, filter the queryset to only include
        projects that the user is a contributor of.
        """
        if not self.request.user.is_staff:
            # Filter the queryset to only include projects that
            # the user is a contributor of
            return self.queryset.filter(
                project_contributors__user=self.request.user)

        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        """
        Create a new project.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        proj = serializer.save()

        # Add the user as a contributor to the project
        Contributor.objects.create(user=request.user, project=proj, role="A")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Contributor model.
    check authentication for the user.
    add new contributor to the project.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, ContributorPermission]

    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        """
        Get the list of contributors.
        If the user is not staff, filter the queryset to only include
        contributors that work on the same project as the user.
        """
        if self.request.user.is_staff:
            return super().get_queryset()
        # Filter the queryset to only include contributors that
        # work on the same project as the user
        projects_user = self.request.user.contributed_projects.all()
        contributors = Contributor.objects.filter(project__in=projects_user)
        return contributors


class IssueViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Issue model.
    check authentication for the user.
    add new issue to the project if the user is the author.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IssueCommentAuthor]
    serializer_class = IssueUserSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'put',
                         'patch', 'delete', 'head',
                         'options']

    def get_queryset(self):
        issues = Issue.objects.filter(
            project__uuid=self.kwargs['project_uuid'])
        if not self.request.user.is_staff:
            # Filter the queryset to only include issues that
            # the user is a contributor or author on issues
            issues = issues.filter(
                project__project_contributors__user=self.request.user)
            return issues

        return issues

    def create(self, request, *args, **kwargs):
        # Create a new issue.
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        data['author'] = request.user
        # Overide the save of serializer
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Comment model.
    Check authentication for the user.
    Add new comment to the issue if the user is the author.
    Check permissions, authorization to create, update or delete.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IssueCommentAuthor]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'put',
                         'patch', 'delete', 'head',
                         'options']

    def get_queryset(self):
        comments = Comment.objects.filter(
            issue__uuid=self.kwargs['issue_uuid'])
        if not self.request.user.is_staff:
            # Filter the queryset to only include comments that
            # the user is a contributor or author on comments issue
            comments = comments.filter(
                issue__project__project_contributors__user=self.request.user
            )
            return comments
        return comments

    def create(self, request, *args, **kwargs):
        # Create a new comment.
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        data['author'] = request.user
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
