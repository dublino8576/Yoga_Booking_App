from django.db import models
from django.utils.text import slugify

# Create your models here.

class Yoga_Type(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title # primary key is shown as string representation so when we use foreign key to this model, the title will be shown instead of the id (for example in the admin interface or in a template)
    
class Teacher(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    yoga_types = models.ManyToManyField(Yoga_Type, related_name='teachers') #create a many-to-many relationship between Teacher and Yoga_Type models, with a related name of 'teachers' for reverse lookups (reverse lookups allow you to access the related objects from the other side of the relationship)
    slug = models.SlugField(unique=True, blank=True) #add a slug field to the Teacher model, which will be used to create SEO-friendly URLs for teacher profiles (the slug will be automatically generated based on the teacher's name and surname when the object is saved)
    email = models.EmailField(unique=True)
    bio = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} {self.surname}'
    
    def save(self, *args, **kwargs):
        was_active = True
        if self.pk: #pk is the primary key of the object, if it exists it means the object is being updated, not created for the first time
            was_active = Teacher.objects.filter(pk=self.pk).values_list('is_active', flat=True).first() #check the current value of is_active in the database before saving the object, so you can compare it with the new value of is_active after saving and if it changed from True to False, you can cancel all active classes of that teacher (this is necessary because if you check the value of is_active after saving, it will already be updated to the new value, so you need to check it before saving)

        self.slug = f'{self.name.lower()}-{self.surname.lower()}'
        super().save(*args, **kwargs) #override the save method to automatically generate a slug based on the teacher's name and surname, and then call the parent class's save method to save the object to the database (works also if new teacher is created outside of the admin interface, for example in a view or a script)

        # If teacher is deactivated, automatically cancel all their active classes.
        if was_active and not self.is_active:
            self.classes.filter(is_cancelled=False).update(is_cancelled=True)
    
    class Meta:
        ordering = ['-created_at']
        #create ordering by newest created_at first


#####################################################


class Yoga_Class(models.Model):
    yoga_types = models.ForeignKey(Yoga_Type, on_delete=models.CASCADE, related_name='classes') #create a foreign key relationship between Yoga_Class and Yoga_Type models, with a related name of 'classes' for reverse lookups
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='classes') #create a foreign key relationship between Yoga_Class and Teacher models, with a related name of 'classes' for reverse lookups
    slug = models.SlugField(unique=True, blank=True) #add a slug field to the Yoga_Class model, which will be used to create SEO-friendly URLs for class detail pages (the slug will be automatically generated based on the yoga type title when the object is saved)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_cancelled = models.BooleanField(default=False)
    repeats_weekly = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=10.00) #add a price field to the Yoga_Class model, which will be used to store the price of each class for payment

    def save(self, *args, **kwargs):
        if not self.slug:
            #generates a unique slug only if the slug field is empty (which means the object is being created for the first time, not updated).
            base = f"{self.yoga_types.title} {self.teacher.slug} {self.date}"
            base_slug = slugify(base) #slugify the base string to create a URL-friendly slug (the slugify function converts the string to lowercase, replaces spaces with hyphens, and removes any special characters)
            slug = base_slug #initialize the slug variable with the base slug
            counter = 1

            while Yoga_Class.objects.filter(slug=slug).exists(): #check if a Yoga_Class with the same slug already exists in the database, and if it does, append a counter to the slug until a unique slug is found (this ensures that even if there are multiple classes with the same yoga type, teacher, and date, they will still have unique slugs)
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs) #if slug already exists skip slug generation and just save the object to the database


    class Meta:
        verbose_name_plural = 'Yoga Classes'
        ordering = ['date', 'start_time', 'yoga_types__title']
        #create ordering by earliest date and start_time first