from django.db import models


class Observatory(models.Model):
    aws_code = models.IntegerField(unique=True)
    aws_type_name = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    lng = models.FloatField()
    lat = models.FloatField()
    address = models.CharField(max_length=300)


class WeatherData(models.Model):
    timestamp = models.CharField(max_length=16, default='000000000000')
    observatory = models.ForeignKey(Observatory, on_delete=models.CASCADE)
    wind_direction_value = models.FloatField(default=-999)
    wind_direction_str = models.CharField(max_length=5)
    wind_speed = models.FloatField(default=-999)
    temperature = models.FloatField(default=-999)
    precipitation = models.FloatField(default=-999)
    humidity = models.FloatField(default=-999)


class AirPollution(models.Model):
    timestamp = models.CharField(max_length=16, default='000000000000')
    observatory = models.ForeignKey(Observatory, on_delete=models.CASCADE)
    pm10 = models.FloatField(default=-999)
    pm25 = models.FloatField(default=-999)
    o3 = models.FloatField(default=-999)
    no2 = models.FloatField(default=-999)
    co = models.FloatField(default=-999)
    so2 = models.FloatField(default=-999)
