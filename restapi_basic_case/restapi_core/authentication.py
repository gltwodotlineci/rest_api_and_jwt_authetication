# myapp/authentication.py
import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomUser, Project


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])  # use your same secret
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        user_id = payload.get('id')
        if not user_id:
            raise AuthenticationFailed('Invalid token payload')

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('User not found')

        return (user, None)


class ProjectOwnerAuthentication(BaseAuthentication):
    """
    Custom authentication class to check if the user is the owner of the project.
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None


        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        user_id = payload.get('id')
        if not user_id:
            raise AuthenticationFailed('Invalid token payload')

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('User not found')

        user.projects = user.project_set.all()
        # Check if the user is the owner of the project
        project_id = request.data.get('project_id')
        if project_id:
            try:
                project = user.projects.get(pk=project_id)
            except Project.DoesNotExist:
                raise AuthenticationFailed('User is not the owner of the project')

        return (user, None)

