from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from notes.models import Category


class Task(models.Model):
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    is_completed = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, blank=True, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_completed', 'due_date', '-priority']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('planner:task_detail', kwargs={'pk': self.pk})

    @property
    def is_overdue(self):
        from django.utils import timezone
        return bool(self.due_date and not self.is_completed and self.due_date < timezone.localdate())
