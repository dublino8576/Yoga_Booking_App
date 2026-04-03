from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Booking

# Create your views here.

@login_required
def bookings(request):
    today = timezone.localdate()
    if request.method == 'GET':
        upcoming_bookings = Booking.objects.filter(user=request.user, yoga_class__date__gte=today, status__in=[1, 2]).order_by('-yoga_class__date', '-yoga_class__start_time') #get the booking for the current user, this will return a queryset of Booking objects that are associated with the currently logged-in user (the user is accessed through request.user, which is provided by Django's authentication system). Yoga classes that are in the past (yoga_class__date__gte=today) are excluded from the queryset, so only upcoming bookings will be included in the results. (class__date__gt=today is a filter that checks if the date of the yoga class associated with the booking is greater than the current date, which means the class is in the future). The results are ordered by the date and start time of the yoga class in descending order, so the most recent upcoming classes will be shown first.

        active_bookings = upcoming_bookings.filter(status=1) #filter the booking queryset to get only the active bookings (status=1 means confirmed bookings)
        cancelled_bookings = upcoming_bookings.filter(status=2) #filter the booking queryset to get only the cancelled bookings (status=2 means cancelled bookings)

        context = {
            'active_bookings': active_bookings,
            'cancelled_bookings': cancelled_bookings}

        
        return render(request, 'bookings/booking_list.html', context) #render the booking_list.html template and pass the booking querysets as context to the template (the context is a dictionary that contains the data that will be used in the template, in this case we are passing the booking querysets with the keys 'active_bookings' and 'cancelled_bookings')
    
