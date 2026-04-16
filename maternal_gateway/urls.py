"""
URL configuration for maternal_gateway project.

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
from core_api import views as frontend_views
from django.http import JsonResponse
from django.shortcuts import render

def custom_handler404(request, exception):
    if request.path.startswith('/api/'):
        return JsonResponse({'error': 'The requested API route was not found.', 'status': 404}, status=404)
    return render(request, '404.html', status=404)

handler404 = 'maternal_gateway.urls.custom_handler404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('core_api.urls')),
    
    # Frontend Pages
    path('', frontend_views.home_view, name='home'),
    path('surgical', frontend_views.surgical_view, name='surgical'),
    path('login', frontend_views.login_view, name='login'),
    path('settings', frontend_views.settings_view, name='settings'),
    path('help', frontend_views.help_view, name='help'),
]
