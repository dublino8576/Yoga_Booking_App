#urls
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Booking.as_view(), name='booking_list')
]