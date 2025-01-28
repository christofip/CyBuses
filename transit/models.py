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
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    line_name = models.CharField(max_length=80, blank=True)
    route_name = models.CharField(max_length=120, blank=True)
    direction = models.CharField(max_length=80, blank=True)
    length = models.FloatField(null=True, blank=True)
    first_stop = models.CharField(max_length=80, blank=True)
    last_stop = models.CharField(max_length=80, blank=True)
    stops_list = models.TextField(blank=True)  # Comma-separated list from GTFS
    geometry = models.LineStringField(srid=4326)
    color = models.CharField(max_length=7, default='#666666')
    
    # Weekday schedule
    weekday_start = models.TimeField(null=True, blank=True)
    weekday_end = models.TimeField(null=True, blank=True)
    weekday_morning_frequency = models.CharField(max_length=80, blank=True)
    weekday_afternoon_frequency = models.CharField(max_length=80, blank=True)
    weekday_trips = models.CharField(max_length=80, blank=True)
    
    # Saturday schedule
    saturday_start = models.TimeField(null=True, blank=True)
    saturday_end = models.TimeField(null=True, blank=True)
    saturday_morning_frequency = models.CharField(max_length=80, blank=True)
    saturday_afternoon_frequency = models.CharField(max_length=80, blank=True)
    saturday_trips = models.CharField(max_length=80, blank=True)
    
    # Holiday schedule
    holiday_start = models.TimeField(null=True, blank=True)
    holiday_end = models.TimeField(null=True, blank=True)
    holiday_morning_frequency = models.CharField(max_length=80, blank=True)
    holiday_afternoon_frequency = models.CharField(max_length=80, blank=True)
    holiday_trips = models.CharField(max_length=80, blank=True)
    
    stops = models.ManyToManyField(Stop, through='RouteStop', related_name='routes')

    def __str__(self):
        return f"Route {self.route_id} - {self.line_name}"

class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    sequence = models.IntegerField()  # Order of stops in the route

    class Meta:
        ordering = ['route', 'sequence']
        unique_together = [['route', 'sequence'], ['route', 'stop']]
        indexes = [
            models.Index(fields=['route', 'sequence']),
        ]

    def __str__(self):
        return f"{self.route} - Stop {self.sequence}: {self.stop}"
