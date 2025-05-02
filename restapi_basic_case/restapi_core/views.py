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
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

    serializer_class = ProjectSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
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
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'delete', 'head', 'options']

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        # Filter the queryset to only include contributors that
        return self.queryset.filter(user=self.request.user)


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueUserSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'delete', 'head', 'options']


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'uuid'
    http_method_names = ['get', 'delete', 'head', 'options']
