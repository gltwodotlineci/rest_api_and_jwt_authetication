from datetime import datetime, timezone, timedelta
import jwt
# from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CustomUser, Project, Contributor, Issue, Comment
from .serializers import CustomUserSerializer, ProjectSerializer, \
    ContributorSerializer, IssueUserSerializer, CommentSerializer
from rest_framework.exceptions import AuthenticationFailed
from .authentication import CustomJWTAuthentication
from .permissions import IssueContributorOrAuthor, ProjectPermission
from django.db.models import Q


def refacto_list_objects(model, serializer_model) -> dict:
    """
    refacto the creation of the list for the viewset:
    """
    queryset = model.objects.all()
    obj_serialized = serializer_model(queryset, many=True)
    objects = obj_serialized.data
    return objects


class CustomUserViewSet(viewsets.ViewSet):

    def list(self, request):
        # users = refacto_list_objects(CustomUser, CustomUserSerializer)
        # return Response(users)
        queryset = CustomUser.objects.all()
        obj_serialized = CustomUserSerializer(queryset, many=True)
        users = obj_serialized.data
        return Response(users)

    def retrieve(self, request, pk=None):
        pass

    def create(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


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
    permission_classes = [IsAuthenticated]

    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        # Filter the queryset to only include contributors that
        # work on the same project as the user
        user = self.request.user.contributed_projects.all()
        contributors = Contributor.objects.filter(project__in=user)
        return contributors

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if not self.request.user.is_staff:
            data = serializer.validated_data

            proj = data.get('project')
            usr_contrib = Contributor.objects.filter(
                Q(user__in=proj.contributors.all()) & Q(role='A'))
            if request.user != usr_contrib.last().user:
                msg0 = "You're not authorized to add"
                msg1 = " contributors to this project."
                message = f"{msg0} {msg1}"
                return Response({'error': message},
                                status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        destroy an existing contributor.
        """
        instance = self.get_object()

        if instance.user == self.request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_200_OK)

        if not self.request.user.is_staff:

            author = Contributor.objects.filter(Q(project=instance.project)
                                                & Q(role='A')).first()

            if request.user != author.user:
                msg = "You're not authorized to remove this contributor"
                return Response({'error': msg},
                                status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class IssueViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Issue model.
    check authentication for the user.
    add new issue to the project if the user is the author.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IssueContributorOrAuthor]
    queryset = Issue.objects.all()
    serializer_class = IssueUserSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'put',
                         'patch', 'delete', 'head',
                         'options']

    def get_queryset(self):
        if not self.request.user.is_staff:
            # Filter the queryset to only include issues that
            # the user is a contributor or author on issues
            issues = self.queryset.filter(
                Q(project__project_contributors__user=self.request.user) |
                Q(author=self.request.user)
            )
            return issues
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        # Create a new issue.
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        data['author'] = request.user
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            contributors = request.data.get('contributors', [])
            # Check if the users are contributors of the project
            issue = self.get_object()

            existing_contrib = issue.project.contributors.all()
            contribs_id = [str(usr.pk) for usr in existing_contrib]

            if not set(contributors).issubset(set(contribs_id)):
                msg0 = "One or many contriburos you gave is not part"
                msg1 = " of the project."
                msg = f"{msg0} {msg1}"
                return Response({'error': msg},
                                status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Comment model.
    Check authentication for the user.
    Add new comment to the issue if the user is the author.
    Check permissions, authorization to create, update or delete.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'put',
                         'patch', 'delete', 'head',
                         'options']

    """
    def get_queryset(self):
        if not self.request.user.is_staff:
            user = self.request.user
            # Filter the queryset to only include comments that
            # the user is a contributor or author on comments isue
            comments = self.queryset.filter(
                issue__project__project_contributors__user=user
            )

            return comments
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        # Create a new comment.
        serializer = self.get_serializer(data=request.data)
        user = self.request.user
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if not user.is_staff:
            data = serializer.validated_data
            if user != data.get('author'):
                msg = "You're not authorized to add a comment"
                return Response({'error': msg},
                                status=status.HTTP_403_FORBIDDEN)
                issue = data.get('issue')
                if user != issue.contributor.user:
                    msg = "You're not authorized to add a comment"
                    return Response({'error': msg},
                                    status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # update an existing comment.
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)

        if not self.request.user.is_staff:

            if instance.author != self.request.user:
                msg = "You're not authorized to update this comment."
                return Response({'error': msg},
                                status=status.HTTP_403_FORBIDDEN)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        # destroy an existing comment.
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)

        if not self.request.user.is_staff:

            if instance.author != self.request.user:
                msg = "You're not authorized to delete this comment."
                return Response({'error': msg},
                                status=status.HTTP_403_FORBIDDEN)
        serializer.is_valid(raise_exception=True)
        print("Im trying to delete it: ")
        self.perform_destroy(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    """
