#import forms from django
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from pathlib import Path
from django.core.exceptions import ValidationError
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

        if get_user_model().objects.filter(email__iexact=email).exists(): #check against the active auth user model so duplicates are caught even if users were created via get_user_model().

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
    


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User_Account
        fields = ["profile_picture"]
        widgets = {
            "profile_picture": forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/webp"} #restrict file input to only accept JPEG, PNG, and WEBP image formats. This is done by setting the accept attribute of the ClearableFileInput widget to a comma-separated list of MIME types corresponding to the allowed image formats. This helps ensure that users can only upload valid image files for their profile picture.
            )
        }

    def clean_profile_picture(self):
        image = self.cleaned_data.get("profile_picture") #gets the uploaded image file from the cleaned_data dictionary after the form has been submitted and validated. This method is responsible for validating the uploaded profile picture to ensure it meets certain criteria (such as file type and size) before it is saved to the user's account.

        # No new file uploaded; allow keeping current image.
        if not image:
            return image

        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        ext = Path(image.name).suffix.lower()
        if ext not in allowed_extensions:
            raise ValidationError("Only JPG, PNG, or WEBP files are allowed.")

        allowed_mime_types = {"image/jpeg", "image/png", "image/webp"}
        content_type = getattr(image, "content_type", "").lower()
        if content_type not in allowed_mime_types:
            raise ValidationError("Invalid image type. Upload JPG, PNG, or WEBP.")

        max_size_mb = 5
        if image.size > max_size_mb * 1024 * 1024:
            raise ValidationError("Image must be 5MB or smaller.")

        return image