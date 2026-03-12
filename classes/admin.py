from django.contrib import admin #import the admin module from django.contrib
from .models import Yoga_Type, Teacher
# Register your models here.

admin.site.register(Yoga_Type)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'surname', 'email', 'yoga_type__title')
    list_filter = ('is_active',)
    