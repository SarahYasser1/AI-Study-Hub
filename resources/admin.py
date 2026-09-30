from django.contrib import admin
from .models import Resource, ResourceType

@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'resource_type', 'created_at')
    search_fields = ('title', 'description')
