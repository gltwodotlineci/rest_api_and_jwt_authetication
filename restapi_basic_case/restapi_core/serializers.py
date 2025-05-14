from restapi_core.models import CustomUser, Project, Contributor, \
    Issue, Comment
from rest_framework import serializers


# Serializing Customuser
class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'age', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


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

    class Meta:
        model = Contributor
        fields = ['user', 'project', 'role', 'date_joined']


# Serializing Customuser
class IssueUserSerializer(serializers.ModelSerializer):
    contributors = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        required=False,
        allow_null=True
    )


    class Meta:
        model = Issue
        fields = ['contributors',
                  'project',
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
