from django.shortcuts import render, redirect
#import messages#
from django.contrib import messages
from .forms import User_Account_Creation_Form
from django.contrib.auth import logout as auth_logout

# Create your views here.

def accounts(request):
    '''
    View function for serving the accounts page. 

    This view will render the accounts template (accounts/accounts.html) which displays information about the user's account and provides options for managing their account settings, such as updating their profile information or changing their password.
    '''

    return render(request, 'accounts/accounts.html')

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