from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class User_Account(User):
    #User model will provide username, email, password, first_name, last_name by default. We just need to extend it with additional fields for role, bio, profile picture, and phone number for the dashboard. We will also add a role field to differentiate between students and teachers. (This will help us to manage permissions and access to certain features in the app.)
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True) #keep ImageField native django field for testing of image upload functionality(using Pillow). Switch to CloudinaryField later if needed for deployment.
    

    class Meta:
        verbose_name_plural = 'User Accounts'

    def __str__(self):
        return self.username