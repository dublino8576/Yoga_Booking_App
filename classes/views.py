from multiprocessing import context

from django.shortcuts import render
from .models import Yoga_Class, Teacher, Yoga_Type
#import generic views
from django.views import generic
# Create your views here.
class Yoga_Class_List(generic.ListView):

    '''
    View function for serving the list of yoga classes with filtering and pagination.
    
    This view will handle GET requests to display a list of yoga classes, and it will also handle filtering the classes based on the date, yoga type, and teacher. The view will use pagination to limit the number of classes displayed per page, and it will optimize the database queries by using select_related to fetch related teacher and yoga type objects in a single query.
    
    '''

    model = Yoga_Class
    template_name = 'classes/class_list.html'
    context_object_name = 'classes'
    paginate_by = 2
    def get_queryset(self):
        queryset = super().get_queryset().select_related('teacher', 'yoga_types') #optimize the query by using select_related to fetch the related teacher and yoga type objects in a single query (this reduces the number of database queries and improves performance)
        date = self.request.GET.get('date')
        yoga_type = self.request.GET.get('yoga_type')
        teacher = self.request.GET.get('teacher')

        #Reads filters from URL query params:
        # ?date=2026-03-16
        # ?yoga_type=1
        # ?teacher=2
        # Applies them to the queryset.
        if date:
            queryset = queryset.filter(date=date) #filter the queryset based on the date parameter from the GET request
        
        if yoga_type:
            queryset = queryset.filter(yoga_types__id=yoga_type) #filter the queryset based on the yoga type parameter from the GET request (the double underscore syntax is used to filter based on a related field, in this case the id of the related yoga type)
        
        if teacher:
            queryset = queryset.filter(teacher__id=teacher) 
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # 1) call the parent class's get_context_data method to get the default context data so you have access to the default context variables like page_obj and paginator.
        # 2)builds the context for the template by adding the list of active teachers, yoga types, and the selected filters from the GET request (this allows you to display the filter options and the selected filters in the template)
        context["teachers"] = Teacher.objects.filter(is_active=True).order_by("surname", "name")
        context["yoga_types"] = Yoga_Type.objects.order_by("title")
        # 3) you only need the data from teacher table and yoga type table as you already have the filtered classes in the context variable "classes" in **kwargs. 
        context["selected_date"] = self.request.GET.get("date", "")
        context["selected_teacher"] = self.request.GET.get("teacher", "")
        context["selected_yoga_type"] = self.request.GET.get("yoga_type", "")
        # 4) GET method sent by the user choosing the filters in the template, and we add the selected filters to the context so we can display them in the template for a better user experience so they know which filters are currently applied. (it does not query the database again, it just reads the selected filters from the GET request and adds them to the context)
        params = self.request.GET.copy() #copy the GET parameters from the request so you can modify them without affecting the original GET parameters (this is necessary because you want to remove the page parameter from the GET parameters when generating the pagination links, so you need to work with a copy of the GET parameters)
        params.pop("page", None)  # avoid duplicate page param
        context["active_filters_query"] = params.urlencode() #encode the modified GET parameters as a query string so you can use it in the pagination links to preserve the selected filters when navigating through the pages (this allows you to keep the selected filters applied when you click on the pagination links, so you don't lose the filters when you navigate to the next page)
        return context

    '''
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context[""] = 
        return context
    
    '''