from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseNotAllowed
from django.urls import reverse
import stripe

from .models import Booking
from classes.models import Yoga_Class
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
    
@login_required
def create_checkout_session(request):
    """Create a Stripe Checkout Session for booking a yoga class."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    yoga_class_id = request.POST.get("yoga_class_id")
    yoga_class = get_object_or_404(Yoga_Class, id=yoga_class_id)

    # Check if class is cancelled
    if yoga_class.is_cancelled:
        messages.error(request, "This class is cancelled.")
        return redirect("class_list")

    # Check if user already has an active booking for this class
    already_booked = Booking.objects.filter(
        user=request.user,
        yoga_class=yoga_class,
        status__in=[0, 1],
    ).exists()
    if already_booked:
        messages.info(request, "You already have a booking for this class.")
        return redirect("my_profile")

    # Check if class is at capacity
    confirmed_count = Booking.objects.filter(
        yoga_class=yoga_class, status=1
    ).count()
    if confirmed_count >= yoga_class.capacity:
        messages.error(request, "This class is fully booked.")
        return redirect("class_list")

    # Create booking with transaction to ensure atomicity which means that if any part of the process fails (for example, if there is an error creating the Stripe session), the entire transaction will be rolled back and the database will not be left in an inconsistent state (for example, a booking created without a corresponding Stripe session or a Stripe session created without a corresponding booking)
    with transaction.atomic():
        booking = Booking.objects.create(
            user=request.user,
            yoga_class=yoga_class,
            status=0,
            currency="GBP",
            amount_paid=yoga_class.price,
        )

        # Build URLs for redirects
        success_url = request.build_absolute_uri(reverse("checkout_success"))
        cancel_url = request.build_absolute_uri(reverse("checkout_cancel"))

        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            mode="payment",
            customer_email=request.user.email or None,
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "unit_amount": int(yoga_class.price * 100),
                        "product_data": {
                            "name": f"{yoga_class.yoga_types.title} - {yoga_class.teacher.surname}",
                            "description": f"Class on {yoga_class.date} at {yoga_class.start_time}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=cancel_url,
            metadata={
                "booking_id": str(booking.id),
                "user_id": str(request.user.id),
                "class_id": str(yoga_class.id),
            },
        )

        # Save Stripe session ID on booking
        booking.stripe_checkout_id = session.id
        booking.save(update_fields=["stripe_checkout_id"])

    # Redirect to Stripe Checkout
    return redirect(session.url, permanent=False)


@login_required
def checkout_success(request):
    """Handle successful payment and confirm booking."""
    session_id = request.GET.get("session_id")

    if not session_id:
        messages.error(request, "Invalid session.")
        return redirect("class_list")

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        # Get booking using Stripe session ID
        booking = get_object_or_404(Booking, stripe_checkout_id=session_id)

        # Verify the session has been paid
        if session.payment_status == "paid":
            booking.status = 1  # Confirmed
            booking.stripe_payment_intent = session.payment_intent
            booking.save(update_fields=["status", "stripe_payment_intent"])
            messages.success(
                request,
                f"Booking confirmed! Your class is on {booking.yoga_class.date}.",
            )
        else:
            messages.warning(request, "Payment not completed.")

    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {str(e)}")

    return redirect("my_profile")


@login_required
def checkout_cancel(request):
    """Handle cancelled payment."""
    messages.info(request, "Payment cancelled. Your booking was not confirmed.")
    return redirect("class_list")

@login_required
def cancel_booking(request, booking_id): #booking id needed to identify which booking to cancel, this will be passed in the URL when the user clicks the cancel button for a specific booking in their profile page
    """Allow users to cancel their confirmed bookings, this view will handle the cancellation of a booking when a user clicks the cancel button for a specific booking in their profile page. It will check if the booking is eligible for cancellation (only confirmed future bookings can be cancelled), update the booking status to cancelled, and set the cancelled_at timestamp. The user will then be redirected back to their profile page with a success message confirming the cancellation. If the booking cannot be cancelled (for example, if it's already cancelled or if it's a past booking), an error message will be shown instead."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # only confirmed future bookings can be cancelled
    if booking.status != 1:
        messages.error(request, "Only confirmed bookings can be cancelled.")
        return redirect("my_profile")

    if booking.yoga_class.date < timezone.localdate():
        messages.error(request, "Past bookings cannot be cancelled.")
        return redirect("my_profile")

    booking.status = 2
    booking.cancelled_at = timezone.now()
    booking.save(update_fields=["status", "cancelled_at"])

    messages.success(request, "Booking cancelled successfully.")
    return redirect("my_profile")