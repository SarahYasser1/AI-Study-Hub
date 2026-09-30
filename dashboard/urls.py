from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('export/tasks/pdf/', views.export_tasks_pdf, name='export_tasks_pdf'),
]
