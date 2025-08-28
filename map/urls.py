# map/map/urls.py
from django.contrib import admin
from django.urls import path, include
from map_app.views import map_page, map_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', map_page, name='map_page'),  # Главная страница с картой
    path('api/map_objects/', map_api, name='map_api'), # API для работы с объектами
]