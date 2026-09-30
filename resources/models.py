from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from notes.models import Category


class ResourceType(models.Model):
    """e.g. Video, Article, Book, Course, Tool."""
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text='CSS icon class or emoji')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Resource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    link = models.URLField()
    resource_type = models.ForeignKey(ResourceType, on_delete=models.SET_NULL, null=True, related_name='resources')
    categories = models.ManyToManyField(Category, blank=True, related_name='resources')
    thumbnail = models.ImageField(upload_to='resource_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('resources:resource_detail', kwargs={'pk': self.pk})
