# map/map_app/models.py
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
    trip_name = models.CharField(max_length=255, default='Поездка 1')
    
    def __str__(self):
        return self.name if self.name else f'Объект #{self.pk}'

    class Meta:
        verbose_name = "Объект на карте"
        verbose_name_plural = "Объекты на карте"