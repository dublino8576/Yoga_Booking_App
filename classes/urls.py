#urls.py
from django.contrib import admin
from django.urls import path, include
from classes import views

urlpatterns = [
    path('', views.Yoga_Class_List.as_view(), name='class_list'),
]