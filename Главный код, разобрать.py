# geodjango_map/manage.py
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geodjango_map.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

# --------------------------------------------------------------------------

# geodjango_map/geodjango_map/settings.py
"""
Django settings for geodjango_map project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@e^g-n5m+j6x7^j8_s*w5b-m^#o_7-w!t=q%f@7g$4+v#f_c1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # Активация GeoDjango
    'map_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'geodjango_map.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'geodjango_map.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# !!! ВАЖНО: ЗАМЕНИТЕ ЭТИ ПЛЕЙСХОЛДЕРЫ НА ВАШИ ДАННЫЕ !!!
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'db_name',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------

# geodjango_map/geodjango_map/urls.py
from django.contrib import admin
from django.urls import path, include
from map_app.views import map_page, map_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', map_page, name='map_page'),  # Главная страница с картой
    path('api/map_objects/', map_api, name='map_api'), # API для работы с объектами
]

# --------------------------------------------------------------------------

# geodjango_map/map_app/models.py
from django.contrib.gis.db import models

class MapObject(models.Model):
    """
    Модель для хранения геометрических объектов на карте.
    """
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    # Геометрическое поле. GeometryField может хранить любой тип геометрии.
    geometry = models.GeometryField(srid=4326, verbose_name="Геометрия")
    photo_url = models.URLField(blank=True, null=True, verbose_name="URL фотографии")

    def __str__(self):
        return self.name if self.name else f'Объект #{self.pk}'

    class Meta:
        verbose_name = "Объект на карте"
        verbose_name_plural = "Объекты на карте"

# --------------------------------------------------------------------------

# geodjango_map/map_app/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.serializers import serialize
from django.contrib.gis.geos import GEOSGeometry

from .models import MapObject

def map_page(request):
    """
    Отображает главную страницу с картой.
    """
    return render(request, 'map.html')

def map_api(request):
    """
    API для работы с объектами на карте.
    - GET: возвращает все объекты в формате GeoJSON.
    - POST: сохраняет новый объект.
    """
    if request.method == 'GET':
        # Сериализуем все объекты из базы данных в формат GeoJSON
        queryset = MapObject.objects.all()
        # use_natural_primary_keys=True
        geojson_data = serialize('geojson', queryset, geometry_field='geometry', fields=('name', 'description', 'photo_url'))
        return JsonResponse(json.loads(geojson_data), safe=False)

    elif request.method == 'POST':
        try:
            # Загружаем JSON-тело запроса
            data = json.loads(request.body.decode('utf-8'))
            
            # Извлекаем тип и координаты геометрии
            geom_type = data['geometry']['type']
            coords = data['geometry']['coordinates']

            # Создаем объект GEOSGeometry
            # GeoJSON формат.
            geom = GEOSGeometry(json.dumps({'type': geom_type, 'coordinates': coords}))
            
            # Извлекаем свойства объекта
            properties = data.get('properties', {})
            name = properties.get('name', 'Новый объект')
            description = properties.get('description', '')
            photo_url = properties.get('photo_url', '')

            # Создаем и сохраняем новый объект в базе данных
            new_object = MapObject.objects.create(
                name=name,
                description=description,
                geometry=geom,
                photo_url=photo_url
            )
            
            # Сериализуем созданный объект и возвращаем ответ
            geojson_object = serialize('geojson', [new_object], geometry_field='geometry', fields=('name', 'description', 'photo_url'))
            return JsonResponse(json.loads(geojson_object), status=201)

        except (json.JSONDecodeError, KeyError) as e:
            return JsonResponse({'error': f'Неверный формат данных: {e}'}, status=400)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

# --------------------------------------------------------------------------

# geodjango_map/map_app/templates/map.html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Интерактивная карта</title>
    <!-- Подключение Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIINfBI87S2C7Z807T39n3wK0lqj/w/uL7w=" crossorigin="" />
    <!-- Подключение Leaflet.draw CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        #map {
            flex-grow: 1;
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    
    <!-- Подключение Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20n69zI8L9+w/jR+j8qI34U87G8P6G8E6n9C7O0F6yM=" crossorigin=""></script>
    <!-- Подключение Leaflet.draw JS -->
    <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
    <!-- Подключение нашего кастомного JS -->
    <script src="/static/js/main.js"></script>

</body>
</html>

# --------------------------------------------------------------------------

# geodjango_map/map_app/static/js/main.js
// Функция для получения CSRF-токена из куки
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {

    // Инициализация карты
    const map = L.map('map').setView([55.7558, 37.6173], 13); // Координаты Москвы

    // Добавление слоя OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Слой для хранения нарисованных объектов
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Настройка панели инструментов для рисования
    const drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polygon: true,
            polyline: true,
            rectangle: false,
            circle: false,
            marker: true,
            circlemarker: false,
        }
    });
    map.addControl(drawControl);

    // Добавление GeoJSON объектов на карту
    function addGeoJSONToMap(geojson) {
        L.geoJSON(geojson, {
            onEachFeature: function (feature, layer) {
                // Создание всплывающего окна с информацией об объекте
                let popupContent = `
                    <h4>${feature.properties.name || 'Название не указано'}</h4>
                    <p>${feature.properties.description || 'Описание не указано'}</p>
                `;
                
                if (feature.properties.photo_url) {
                    popupContent += `<img src="${feature.properties.photo_url}" style="max-width:200px; max-height:200px;">`;
                }

                popupContent += `<hr><button onclick="addPhoto('${feature.id}')">Добавить фото</button>`;

                layer.bindPopup(popupContent);
            }
        }).addTo(map);
    }

    // Загрузка объектов из базы данных при загрузке страницы
    fetch('/api/map_objects/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Не удалось загрузить данные карты');
            }
            return response.json();
        })
        .then(data => {
            console.log('Загруженные данные:', data);
            addGeoJSONToMap(data);
        })
        .catch(error => console.error('Ошибка:', error));

    // Обработчик события, когда пользователь закончил рисовать объект
    map.on(L.Draw.Event.CREATED, function (e) {
        const layer = e.layer;
        const geojson = layer.toGeoJSON();
        drawnItems.addLayer(layer);

        // Отправка GeoJSON данных на сервер Django
        const csrftoken = getCookie('csrftoken');
        fetch('/api/map_objects/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(geojson),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(JSON.stringify(err)); });
            }
            return response.json();
        })
        .then(data => {
            console.log('Успешно сохранено:', data);
            // Можно обновить карту, чтобы отобразить новый объект
            // Обычно, если есть другие пользователи, лучше перезагрузить все данные
            // Но для простоты мы просто добавим новый объект
        })
        .catch(error => {
            console.error('Ошибка при сохранении:', error);
            alert('Ошибка при сохранении объекта: ' + error.message);
        });
    });

    // Функция-плейсхолдер для добавления фото
    window.addPhoto = function(featureId) {
        alert(`Функционал добавления фото для объекта с ID ${featureId} пока не реализован.`);
        // Здесь можно было бы открыть модальное окно с формой загрузки
    };
});
