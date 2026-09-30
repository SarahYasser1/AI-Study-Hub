from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('new/', views.conversation_detail, name='conversation_new'),
    path('<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('<int:pk>/send/', views.send_message, name='send_message'),
    path('<int:pk>/delete/', views.conversation_delete, name='conversation_delete'),
]
