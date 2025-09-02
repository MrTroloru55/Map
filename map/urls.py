# map/map/urls.py
from django.contrib import admin
from django.urls import path, include

from map_app import views
from map_app.views import map_page, get_map_objects, create_map_object 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.map_page, name='map_page'),
    path('api/map_objects/get/', views.get_map_objects, name='get_map_objects'),
    path('api/map_objects/create/', views.create_map_object, name='create_map_object'),
]