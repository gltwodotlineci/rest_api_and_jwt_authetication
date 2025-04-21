from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import CustomUser, Project, Contributor, Issue, Comment
from .serializers import CustomUserSerializer, ProjectSerializer,\
    ContributorSerializer, IssueUserSerializer, CommentSerializer

# refacto the creation of the list for the viewset:
def refacto_list_objects(model, serializer_model)-> dict:
    queryset = model.objects.all()
    obj_serialized = serializer_model(queryset, many=True)
    objects = obj_serialized.data
    return objects


class CustomUserViewSet(viewsets.ViewSet):

    def list(self, request):
        users = refacto_list_objects(CustomUser, CustomUserSerializer)
        return Response(users)


    def retrive(self, request, pk=None):
        pass


    def create(self, request):
        pass


    def update(self, request, pk=None):
        pass


    def destroy(self, request, pk=None):
        pass


class ProjectViewSet(viewsets.ViewSet):

    def list(self, request):
        projects = refacto_list_objects(Project, ProjectSerializer)
        return Response(projects)


    def retrive(self, request, pk=None):
        pass


    def create(self, request):
        pass


    def update(self, request, pk=None):
        pass


    def destroy(self, request, pk=None):
        pass


class ContributorViewSet(viewsets.ViewSet):

    def list(self, request):
        contributors = refacto_list_objects(Contributor,
                                            ContributorSerializer)

        return Response(contributors)


    def retrive(self, request, pk=None):
        pass


    def create(self, request):
        pass


    def update(self, request, pk=None):
        pass


    def destroy(self, request, pk=None):
        pass


class IssueViewSet(viewsets.ViewSet):

    def list(self, request):
        issues = refacto_list_objects(Issue, IssueUserSerializer)
        return Response(issues)


    def retrive(self, request, pk=None):
        pass


    def create(self, request):
        pass


    def update(self, request, pk=None):
        pass


    def destroy(self, request, pk=None):
        pass


class CommentViewSet(viewsets.ViewSet):

    def list(self, request):
        comments = refacto_list_objects(Comment, CommentSerializer)
        return Response(comments)


    def retrive(self, request, pk=None):
        pass


    def create(self, request):
        pass


    def update(self, request, pk=None):
        pass


    def destroy(self, request, pk=None):
        pass
