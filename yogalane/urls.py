"""
URL configuration for yogalane project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static #for serving media files in development (we will switch to Cloudinary for media file hosting in production, but this is fine for development and testing of image upload functionality using Pillow).

urlpatterns = [
    path('', include('pages.urls')),
    path('classes/', include('classes.urls'), name='class_list'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls'), name='accounts'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
