from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from uuid import uuid4


class CustomUser(AbstractUser):
    uuid = models.UUIDField(primary_key=True,
                            unique=True,
                            default=uuid4,
                            editable=False)
    email = models.EmailField(max_length=100,
                              unique=True,
                              verbose_name='email')
    age = models.PositiveSmallIntegerField(verbose_name="Age",
                                           validators=[MinValueValidator(15)],
                                           null=True,
                                           blank=True)
    time_created = models.DateTimeField(auto_now_add=True)


class Project(models.Model):
    uuid = models.UUIDField(primary_key=True,
                            unique=True,
                            default=uuid4,
                            editable=False)
    contributors = models.ManyToManyField(CustomUser,
                                          through='Contributor',
                                          related_name='contributed_projects')
    name = models.CharField(max_length=75, unique=True)
    description = models.CharField(max_length=250)
    time_created = models.DateTimeField(auto_now_add=True)
    BACKEND, FRONTEND, IOS, ANDROID = 'B', 'F', 'I', 'A'
    TYPE_PROJECT = [
        (BACKEND, 'Back-End'),
        (FRONTEND, 'Front-End'),
        (IOS, 'IOS'),
        (ANDROID, 'Android')
    ]
    type = models.CharField(max_length=1,
                            choices=TYPE_PROJECT)

    def __str__(self):
        return self.name


class Contributor(models.Model):
    uuid = models.UUIDField(primary_key=True,
                            unique=True,
                            default=uuid4,
                            editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='project_contributions')
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='project_contributors')
    date_joined = models.DateTimeField(auto_now_add=True)

    AUTHOR, CONTRIBUTOR = 'A', 'C'
    ROLE = [
        (AUTHOR, 'Author'),
        (CONTRIBUTOR, 'Contributor')
    ]
    role = models.CharField(max_length=1,
                            choices=ROLE,
                            default=CONTRIBUTOR)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'],
                                    name='unique_user_follow')
        ]


class Issue(models.Model):
    uuid = models.UUIDField(primary_key=True,
                            unique=True,
                            default=uuid4,
                            editable=False)
    # No contributor as FK
    contributor = models.ForeignKey(Contributor,
                                    on_delete=models.CASCADE,
                                    related_name='task')
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='task')
    title = models.CharField(max_length=100, unique=True)

    LOW, MEDIUM, HIGH = 'L', 'M', 'H'
    PRIORITY_TASK = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High')
    ]
    priority = models.CharField(max_length=1,
                                choices=PRIORITY_TASK,
                                )

    BUG, FEATURE, TASK = 'B', 'F', 'T'
    TYPE_PROBLEM = [
        (BUG, 'Bug'),
        (FEATURE, 'Feature'),
        (TASK, 'Task')
    ]
    type_problem = models.CharField(max_length=1,
                                    choices=TYPE_PROBLEM)

    TODO, INPROGRESS, FINISHED = 'TO_DO', 'IN_PROGRESSE', 'FINISHED'
    STATUS_PROGRESS = [
        (TODO, 'To Do'),
        (INPROGRESS, 'In progress'),
        (FINISHED, 'Finished')
    ]
    status_progress = models.CharField(max_length=12,
                                       choices=STATUS_PROGRESS,
                                       default=TODO)
    time_created = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    uuid = models.UUIDField(primary_key=True,
                            unique=True, default=uuid4, editable=False)
    # Add user
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE,
                              related_name='comment')
    description = models.CharField(max_length=190)
    issue_url = models.URLField()
    time_created = models.DateTimeField(auto_now_add=True)
