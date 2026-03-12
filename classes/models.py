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
    yoga_types = models.ManyToManyField(Yoga_Type, related_name='teachers') #create a many-to-many relationship between Teacher and Yoga_Type models, with a related name of 'teachers' for reverse lookups (reverse lookups allow you to access the related objects from the other side of the relationship)
    slug = models.SlugField(null=True, blank=True) #add a slug field to the Teacher model, which will be used to create SEO-friendly URLs for teacher profiles (the slug will be automatically generated based on the teacher's name and surname when the object is saved)
    email = models.EmailField(unique=True)
    bio = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} {self.surname}'
    
    def save(self, *args, **kwargs):
        self.slug = f'{self.name.lower()}-{self.surname.lower()}'
        super().save(*args, **kwargs) #override the save method to automatically generate a slug based on the teacher's name and surname, and then call the parent class's save method to save the object to the database (works also if new teacher is created outside of the admin interface, for example in a view or a script)
    
    class Meta:
        ordering = ['-created_at']
        #create ordering by newest created_at first

