from .models import CustomUser, Project, Contributor, Issue, Comment
from django.contrib import admin


class CustomUserAdmin(admin.ModelAdmin):
    """
    Admin interface for the CustomUser model.
    """
    list_display = ('username',  'pk', 'email', 'age', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'age')
    ordering = ('username',)
    list_per_page = 15


class CotnributorInline(admin.TabularInline):
    """
    Inline admin interface for the Contributor model.
    """
    model = Contributor
    extra = 1
    fields = ('user', 'role')


class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for the Project model.
    """
    list_display = ('name', 'pk', 'description', 'type', 'time_created')
    search_fields = ['name']
    list_filter = ('type', 'time_created')
    ordering = ['-time_created']
    list_per_page = 15
    inlines = [CotnributorInline]

    def has_add_permission(self, request):
        return request.user.is_superuser


class ContributorAdmin(admin.ModelAdmin):
    """
    Admin interface for the Contributor model.
    """
    list_display = ('user', 'pk', 'project', 'date_joined', 'role')
    search_fields = ['user__username', 'project__name']
    list_filter = ('role',)
    ordering = ['-date_joined']
    list_per_page = 15


class IssueAdmin(admin.ModelAdmin):
    """
    Admin interface for the Issue model.
    """
    list_display = ('title', 'pk',
                    'project', 'contributor',
                    'priority', 'type_problem')
    search_fields = ['title']
    list_filter = ('priority',)
    ordering = ['-time_created']
    list_per_page = 15


class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for the Comment model.
    """
    list_display = ('issue', 'pk', 'description')
    search_fields = ['issue']
    list_filter = ('issue',)
    ordering = ['-time_created']
    list_per_page = 15


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Comment, CommentAdmin)
