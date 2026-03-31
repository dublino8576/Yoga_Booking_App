#import forms from django
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
#from django.contrib.auth.forms import AuthenticationForm
from .models import User_Account

class User_Account_Creation_Form(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, help_text='Required. Enter your first name.')
    last_name = forms.CharField(max_length=150, required=True, help_text='Required. Enter your last name.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')

    #username email and password are already required since they are necessary fields for the UserCreationForm. We set

    class Meta(UserCreationForm.Meta):
        model = User_Account #specify the model to use for this form, which is our custom User_Account model that extends the default Django User model.
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        #fields to include in the form. We include username, first_name, last_name, email, password1, password2 (for password confirmation)

    def clean_email(self):
        email = self.cleaned_data.get('email') #get the email from the cleaned_data dictionary

        if User_Account.objects.filter(email=email).exists(): #check if a user with the same email already exists in the database. This is done by querying the User_Account model and filtering for any instances where the email field matches the email provided in the form. If such an instance exists, it means that the email is already in use by another user.

            raise forms.ValidationError("A user with that email already exists.") 
        return email #if the email is unique and does not already exist in the database, return the cleaned email value. This allows the form to proceed with saving the new user account using this unique email address.
    
    def save(self, commit=True):
        user = super().save(commit=False) #delays saving the user instance to the database  until we have set the additional fields (first_name and last_name) that are not included in the default UserCreationForm.

        user.first_name = self.cleaned_data['first_name'] #set the first_name field of the user instance to the value from the form's cleaned_data. CLEANED_DATA is a dictionary that contains the validated form data after it has been cleaned and processed by the form's validation methods. Gets rid of any leading/trailing whitespace and ensures the data is in the correct format.

        user.last_name = self.cleaned_data['last_name'] #set the last_name field of the user instance to the value from the form's cleaned_data.

        user.email = self.cleaned_data['email'] 
        if commit: #if commit is True, save the user instance to the database. This commit is the one from the method save(self, commit=True). 

            user.save()
        return user #return the user instance after saving it to the database. This allows us to use the saved user instance in other parts of our code, such as in views or when creating related objects.
    


