from .models import CustomUser, Project, Contributor
from django.contrib import admin


class CustomUserAdmin(admin.ModelAdmin):
    """
    Admin interface for the CustomUser model.
    """
    list_display = ('username',  'email', 'age', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'age')
    ordering = ('username',)
    list_per_page = 10


class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for the Project model.
    """
    list_display = ('name', 'description', 'type', 'time_created')
    search_fields = ['name']
    list_filter = ('type', 'time_created')
    ordering = ['-time_created']
    list_per_page = 10

    def has_add_permission(self, request):
        return request.user.is_superuser


class ContributorAdmin(admin.ModelAdmin):
    """
    Admin interface for the Contributor model.
    """
    list_display = ('user', 'project', 'date_joined')
    search_fields = ['user__username', 'project__name']
    list_filter = ('date_joined',)
    ordering = ['-date_joined']
    list_per_page = 10


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(Project, ProjectAdmin)
