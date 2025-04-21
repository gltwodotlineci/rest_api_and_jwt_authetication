from restapi_core.models import CustomUser, Project, Contributor,\
    Issue, Comment
from rest_framework import serializers


# Serializing Customuser
class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['username','email', 'age']


# Serializing Customuser
class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['name', 'description', 'user']


# Serializing Customuser
class ContributorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contributor
        fields = ['user', 'project']


# Serializing Customuser
class IssueUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ['contributor',
                  'project',
                  'title',
                  'priority',
                  'type_problem',
                  'status_progress'
                  ]


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['issue', 'description', 'issue_url']
