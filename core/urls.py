from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('search/', views.global_search, name='global_search'),
    path('theme/', views.set_theme, name='set_theme'),
]
