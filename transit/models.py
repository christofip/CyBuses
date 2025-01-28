from django.contrib.gis.db import models

# Create your models here.

class RealtimeVehicle(models.Model):
    VEHICLE_STATUS = [
        ('INCOMING_AT', 'Approaching stop'),
        ('STOPPED_AT', 'Stopped at stop'),
        ('IN_TRANSIT', 'In transit')
    ]

    vehicle_id = models.CharField(max_length=255)
    license_plate = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    bearing = models.FloatField(null=True)
    speed = models.FloatField(null=True)  # m/s
    timestamp = models.DateTimeField()
    trip_id = models.CharField(max_length=255)
    route_id = models.CharField(max_length=255)
    current_status = models.CharField(max_length=20, choices=VEHICLE_STATUS)
    current_stop_sequence = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['vehicle_id']),
            models.Index(fields=['trip_id']),
        ]
        ordering = ['-timestamp']

class Stop(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    description_el = models.CharField(max_length=255)
    description_en = models.CharField(max_length=255)
    location = models.PointField(srid=4326)  # WGS84

    def __str__(self):
        return f"{self.code} - {self.description}"

class Route(models.Model):
    route_id = models.CharField(max_length=80, unique=True)
    geometry = models.LineStringField(srid=4326)
    color = models.CharField(max_length=7, default='#666666')

    def __str__(self):
        return f"Route {self.route_id}"
