from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.create_checkout_session, name="create_checkout_session"),
    path("success/", views.checkout_success, name="checkout_success"),
    path("cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("cancel-booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
]