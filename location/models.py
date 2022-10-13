from django.db import models
from django.utils import timezone


class Location(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=60,
        unique=True
    )
    lat = models.FloatField(
        'Ширина'
    )
    lon = models.FloatField(
        'Долгота'
    )
    date = models.DateField(
        'Дата запроса к Геокодеру',
        default=timezone.now
    )
