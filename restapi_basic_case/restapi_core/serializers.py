from restapi_core.models import CustomUser, Project, Contributor, \
    Issue, Comment
from rest_framework import serializers


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'age', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_age(self, value):
        """
        Check that the age must be inferior to 15
        """
        if value < 15 or value == "":
            message = "The age field must be at least 15 and not empty"
            raise serializers.ValidationError(message)
        return value


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    """
    class Meta:
        model = Project
        fields = ['name', 'description',
                  'contributors', 'type',
                  'time_created']


class ContributorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Contributor model.
    """
    def validate_role(self, value):
        """
        Validate the role field.
        """
        if value != 'C':
            raise serializers.ValidationError("Invalid role")
        return value

    username = serializers.SerializerMethodField()

    class Meta:
        model = Contributor
        fields = ['user', 'username', 'project', 'role', 'date_joined']

    def get_username(self, obj):
        return obj.user.username


class IssueUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ['project',
                  'name',
                  'description',
                  'priority',
                  'type_problem',
                  'status_progress'
                  ]


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['issue', 'description',
                  'author', 'issue_url']
