import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.serializers import serialize
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import MapObject

def map_page(request):
    """
    Отображает главную страницу с картой.
    """
    return render(request, 'map.html')

# GET-запросы разрешены для всех пользователей (даже неавторизованных)
@require_http_methods(["GET"])
def get_map_objects(request):
    """
    API для получения всех объектов карты. Доступен для всех.
    """
    queryset = MapObject.objects.all()
    # Добавлен 'trip_name' в список полей для сериализации
    geojson_data = serialize('geojson', queryset, geometry_field='geometry', fields=('id', 'name', 'description', 'photo_url', 'trip_name'))
    return JsonResponse(json.loads(geojson_data), safe=False)

# POST-запросы разрешены только для авторизованных администраторов
@require_http_methods(["POST"])
@login_required
def create_map_object(request):
    if request.user.is_superuser:
        try:
            data = json.loads(request.body.decode('utf-8'))
            geom = GEOSGeometry(json.dumps(data['geometry']))
            properties = data.get('properties', {})
            trip_name = properties.get('trip_name', 'Поездка 1')
            
            new_object = MapObject.objects.create(
                name=properties.get('name', 'Новый объект'),
                description=properties.get('description', ''),
                geometry=geom,
                photo_url=properties.get('photo_url', ''),
                trip_name=trip_name
            )
            
            geojson_object = serialize('geojson', [new_object], geometry_field='geometry', fields=('id', 'name', 'description', 'photo_url', 'trip_name'))
            return JsonResponse(json.loads(geojson_object), status=201)
        
        except (json.JSONDecodeError, KeyError) as e:
            return JsonResponse({'error': f'Неверный формат данных: {e}'}, status=400)
    else:
        return JsonResponse({'error': 'У вас нет прав для выполнения этого действия'}, status=403)
