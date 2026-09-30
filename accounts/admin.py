from django.contrib import admin
from .models import Profile, EmailVerificationToken

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'field_of_study', 'email_verified')
    search_fields = ('user__username', 'university')

@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'used', 'created_at')
