"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.shortcuts import redirect
import csv

def redirect_to_map(request):
    return redirect('transit:map')

def find_duplicates(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        codes = {}
        duplicates = []
        for row in reader:
            code = row['code']
            if code in codes:
                duplicates.append(code)
            else:
                codes[code] = 1
    return duplicates

duplicates = find_duplicates('data/static/stops.csv')
print(f"Duplicate codes found: {duplicates}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('transit.urls', namespace='transit')),
]
