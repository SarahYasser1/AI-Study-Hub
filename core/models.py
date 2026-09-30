from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):
    """Powers the dashboard's 'Recent Activity' feed."""
    ACTION_CHOICES = [
        ('task_created', 'Task created'),
        ('task_completed', 'Task completed'),
        ('note_created', 'Note created'),
        ('note_updated', 'Note updated'),
        ('resource_added', 'Resource added'),
        ('ai_used', 'Used AI assistant'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.description}'


def log_activity(user, action, description):
    return ActivityLog.objects.create(user=user, action=action, description=description)
