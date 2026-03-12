from django.contrib import admin #import the admin module from django.contrib
from .models import Yoga_Type, Teacher
# Register your models here.

admin.site.register(Yoga_Type)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', 'surname')} #automatically populate the slug field based on the name and surname fields
    list_display = ('name', 'surname', 'email', 'is_active', 'created_at', 'updated_at')

    search_fields = ('name', 'surname', 'email')
    list_filter = ('is_active', 'yoga_types__title') #add a filter for the is_active field and the title of the related yoga types (the double underscore syntax allows you to filter based on fields of related models)
    

