# map/map_app/views.py
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