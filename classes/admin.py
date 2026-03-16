from django.contrib import admin #import the admin module from django.contrib
from .models import Yoga_Type, Teacher, Yoga_Class
from datetime import timedelta
from django.db.models import Q
# Register your models here.

admin.site.register(Yoga_Type)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', 'surname')} #automatically populate the slug field based on the name and surname fields
    list_display = ('name', 'surname', 'email', 'is_active', 'created_at', 'updated_at')

    search_fields = ('name', 'surname', 'email')
    list_filter = ('is_active', 'yoga_types__title') #add a filter for the is_active field and the title of the related yoga types (the double underscore syntax allows you to filter based on fields of related models)
    

@admin.register(Yoga_Class)
class YogaClassAdmin(admin.ModelAdmin):
    list_display = ('yoga_types', 'teacher', 'date', 'start_time', 'end_time', 'capacity', 'is_cancelled', 'repeats_weekly')
    list_filter = ('yoga_types__title', 'teacher', 'date', 'is_cancelled', 'repeats_weekly') 

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'teacher':
            queryset = Teacher.objects.filter(is_active=True)
            object_id = request.resolver_match.kwargs.get('object_id') if request.resolver_match else None

            # Keep currently assigned inactive teacher selectable when editing existing classes.
            if object_id:
                try:
                    yoga_class = Yoga_Class.objects.select_related('teacher').get(pk=object_id)
                    queryset = Teacher.objects.filter(Q(is_active=True) | Q(pk=yoga_class.teacher_id))
                except Yoga_Class.DoesNotExist:
                    pass

            kwargs['queryset'] = queryset.order_by('name', 'surname')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        #when you save a Yoga_Class object (add a row to the Yoga_Class table from outside the model), you call the save model method which saves the object to the database
        #When admin saves a Yoga_Class object it creates the object in the database and the form.cleaned_data contains all the fields but it is not saved yet.
        super().save_model(request, obj, form, change) #now it is saved

        # If the admin checked "repeat weekly" is true
        if form.cleaned_data.get("repeats_weekly"):
            for i in range(1, 4):  # create 4 weeks ahead
                Yoga_Class.objects.create(
                    yoga_types=obj.yoga_types,
                    teacher=obj.teacher,
                    date=obj.date + timedelta(weeks=i),
                    start_time=obj.start_time,
                    end_time=obj.end_time,
                    capacity=obj.capacity,
                    repeats_weekly=True, #makes sure that classes created from the same series are also marked as repeating weekly for a better user experience in the admin interface (add it here so it does not create a loop of creating new classes every time a class is created with repeats_weekly=True)
                )
                #no need to include the slug field because it is automatically generated in the save method of the Yoga_Class model.
