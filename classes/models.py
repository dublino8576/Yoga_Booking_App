from django.db import models

# Create your models here.

class Yoga_Type(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title
    
class Teacher(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} {self.surname}'
    
    class Meta:
        ordering = ['-created_at']
        #create ordering by newest created_at first
        