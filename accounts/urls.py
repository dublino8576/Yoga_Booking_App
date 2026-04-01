#import url from django
from django.urls import path
from accounts import views

#Use a custom LoginView so successful login can show a Django message.

urlpatterns = [
    path('', views.accounts, name='accounts'),
    path('login/', views.CustomLoginView.as_view(template_name="accounts/login.html", next_page='index'), name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register, name='register'),
]