from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.game_view, name='game'),  # Головна сторінка
    path('register/', views.register, name='register'),  # Сторінка реєстрації
    path('login/', auth_views.LoginView.as_view(template_name='game/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('moderator/', views.moderator_view, name='moderator_view'),
    path('superadmin/', views.superadmin_view, name='superadmin_view'),
]