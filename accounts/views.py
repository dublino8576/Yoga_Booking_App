from django.shortcuts import render, redirect
#import messages#
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import User_Account_Creation_Form, ProfilePictureForm
from .models import User_Account
from bookings.models import Booking
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView

# Create your views here.

def accounts(request):
    '''
    View function for serving the accounts page. 

    This view will render the accounts template (accounts/accounts.html) which displays information about the user's account and provides options for managing their account settings, such as updating their profile information or changing their password.
    '''

    return render(request, 'accounts/accounts.html')


class CustomLoginView(LoginView):
    """
    Extend Django LoginView to show a one-time success message after sign in.
    """

    def form_valid(self, form):
        messages.success(self.request, "You have logged in successfully.")
        return super().form_valid(form)

def register(request):

    '''
    View function for serving the user registration page and handling the registration form submission. 

    When a GET request is made to this view, it will render the registration template (accounts/register.html) which contains the registration form for users to fill out. 
    
    When a POST request is made (when the form is submitted), this view will handle the form submission, validate the form data, and create a new user account if the data is valid. If the form data is invalid, it will re-render the registration template with error messages for the user to correct their input.
    '''

    if request.method == 'POST':
        form = User_Account_Creation_Form(request.POST)
        if form.is_valid():
            form.save()
            print("User account created successfully!")
            messages.add_message(request, messages.SUCCESS, "Your account has been created successfully! You can now log in.")
            return redirect('/')
    else:
        form = User_Account_Creation_Form() #creates a form instance from User_Account_Creation_Form when method is GET, which will be empty

    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    '''
    Log out the current user and show a one-time success message, this is a custom logout view which is built differently than the default LogoutView provided by Django's authentication system (usually built in urls.py using auth_views.LogoutView.as_view()).
    '''

    if request.method == 'POST':
        auth_logout(request) #logs out the user by calling the logout function from django.contrib.auth, which clears the user's session and logs them out of the application. This is typically done in response to a POST request to ensure that the logout action is intentional and not triggered by a simple GET request (which could be accidentally triggered by a user clicking a link or refreshing the page).
    messages.add_message(request, messages.SUCCESS, "You have been logged out successfully.")
    return redirect('login')


@login_required #this decorator ensures that only authenticated users can access the my_profile view. If an unauthenticated user tries to access this view, they will be redirected to the login page. This is important for protecting user profile information and ensuring that only logged-in users can view and edit their own profiles.
def my_profile(request):
    try:
        profile_user = request.user.user_account
    except User_Account.DoesNotExist:
        profile_user = User_Account.objects.create(user_ptr=request.user)

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile_user) #gets the submitted form data (request.POST) and any uploaded files (request.FILES) and creates an instance of the ProfilePictureForm with this data.
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile picture has been updated.')
            return redirect('my_profile')
    else:
        form = ProfilePictureForm(instance=profile_user)

    today = timezone.localdate()
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        yoga_class__date__gte=today,
        status__in=[1, 2],
    ).order_by('yoga_class__date', 'yoga_class__start_time') #get the booking for the current user, this will return a queryset of Booking objects that are associated with the currently logged-in user (the user is accessed through request.user, which is provided by Django's authentication system). Yoga classes that are in the past (yoga_class__date__gte=today) are excluded from the queryset, so only upcoming bookings will be included in the results. (class__date__gt=today is a filter that checks if the date of the yoga class associated with the booking is greater than the current date, which means the class is in the future). The results are ordered by the date and start time of the yoga class in descending order, so the most recent upcoming classes will be shown first.

    active_bookings = upcoming_bookings.filter(status=1)#filter the booking queryset to get only the active bookings (status=1 means confirmed bookings)
    cancelled_bookings = upcoming_bookings.filter(status=2)#filter the booking queryset to get only the cancelled bookings (status=2 means cancelled bookings)

    context = {
        'form': form,
        'profile_user': profile_user,
        'active_bookings': active_bookings,
        'cancelled_bookings': cancelled_bookings,
    }

    return render(request, 'accounts/my_profile.html', context)