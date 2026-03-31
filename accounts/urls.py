#import url from django
from django.urls import path
from accounts import views
from django.contrib.auth import views as auth_views
#auth_views is already imported in yogalane/settings.py, but we need to import it here as well to use the LoginView for handling user login functionality in our accounts app. The auth_views module provides built-in views for authentication-related tasks, such as login and logout, which we can utilize in our urls.py to define the URL patterns for these actions.

#no need to create loginview in views.py

urlpatterns = [
    path('', views.accounts, name='accounts'),
    path('login/', auth_views.LoginView.as_view(template_name="accounts/login.html", next_page='index'), name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register, name='register'),
]