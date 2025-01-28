from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import RealtimeVehicle, Stop, Route
from django.utils import timezone
from datetime import timedelta
import requests
from google.transit import gtfs_realtime_pb2
from django.core.serializers import serialize
import json
from django.conf import settings

# Create your views here.

class MapView(TemplateView):
    """Main view for displaying the transit map."""
    template_name = 'transit/map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class RealtimeVehicleView(ListView):
    """List view for displaying realtime vehicle information."""
    model = RealtimeVehicle
    template_name = 'transit/realtime_vehicles.html'
    context_object_name = 'vehicles'
    paginate_by = 50

def realtime_positions(request):
    """Fetch and return realtime vehicle positions from GTFS-RT feed."""
    try:
        response = requests.get(
            settings.GTFS_RT_URL,
            timeout=settings.GTFS_RT_TIMEOUT
        )
        response.raise_for_status()
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        vehicles = []
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                v = entity.vehicle
                vehicles.append({
                    'vehicle_id': v.vehicle.id,
                    'lat': v.position.latitude,
                    'lon': v.position.longitude,
                    'bearing': v.position.bearing,
                    'speed': (v.position.speed * 3.6) if v.position.speed else 0,
                    'route': v.trip.route_id,
                    'updated': timezone.now().isoformat()
                })
        
        return JsonResponse({
            'vehicles': vehicles,
            'expires': (timezone.now() + timedelta(seconds=15)).isoformat()
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_stops_json(request):
    """Return all bus stops as GeoJSON."""
    stops = Stop.objects.all()
    stops_list = [
        {
            'code': stop.code,
            'description': stop.description,
            'description_en': stop.description_en,
            'description_el': stop.description_el,
            'lat': stop.location.y,
            'lon': stop.location.x
        }
        for stop in stops
    ]
    return JsonResponse({'stops': stops_list})

def routes_geojson(request):
    """Return all routes as GeoJSON."""
    routes = Route.objects.all()
    geojson = serialize('geojson', routes, 
                       geometry_field='geometry', 
                       fields=('route_id', 'route_name', 'color', 'direction'))
    return JsonResponse(json.loads(geojson), safe=False)
