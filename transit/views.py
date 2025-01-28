from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Stop, Route, RouteStop, RealtimeVehicle
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
                current_stop_sequence = v.current_stop_sequence if v.HasField('current_stop_sequence') else None
                current_status = v.current_status if v.HasField('current_status') else None
                
                vehicles.append({
                    'vehicle_id': v.vehicle.id,
                    'lat': v.position.latitude,
                    'lon': v.position.longitude,
                    'bearing': v.position.bearing,
                    'speed': (v.position.speed * 3.6) if v.position.speed else 0,
                    'route': v.trip.route_id,
                    'current_stop_sequence': current_stop_sequence,
                    'current_status': current_status,
                    'updated': timezone.now().isoformat()
                })
        
        return JsonResponse({
            'vehicles': vehicles,
            'expires': (timezone.now() + timedelta(seconds=15)).isoformat()
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_stops_json(request):
    """Return bus stops as GeoJSON, optionally filtered by route."""
    route_id = request.GET.get('route_id')
    
    if route_id:
        # Get stops for specific route in sequence order
        route_stops = RouteStop.objects.filter(route__route_id=route_id).select_related('stop').order_by('sequence')
        stops = [rs.stop for rs in route_stops]
    else:
        # Get all stops if no route specified
        stops = Stop.objects.all()

    stops_list = [
        {
            'code': stop.code,
            'description': stop.description,
            'description_en': stop.description_en,
            'description_el': stop.description_el,
            'lat': stop.location.y,
            'lon': stop.location.x,
            'sequence': next((rs.sequence for rs in stop.routestop_set.filter(route__route_id=route_id)) if route_id else None, None)
        }
        for stop in stops
    ]
    return JsonResponse({'stops': stops_list})

def routes_geojson(request):
    """Return all routes as GeoJSON."""
    routes = Route.objects.prefetch_related('routestop_set__stop').all()
    features = []
    
    for route in routes:
        # Get stops in sequence
        route_stops = route.routestop_set.all().order_by('sequence')
        stops_data = [{
            'code': rs.stop.code,
            'description': rs.stop.description,
            'description_en': rs.stop.description_en,
            'description_el': rs.stop.description_el,
            'sequence': rs.sequence,
            'location': [rs.stop.location.x, rs.stop.location.y]
        } for rs in route_stops]
        
        feature = {
            'type': 'Feature',
            'geometry': json.loads(route.geometry.json),
            'properties': {
                'route_id': route.route_id,
                'name': route.name,
                'description': route.description,
                'line_name': route.line_name,
                'route_name': route.route_name,
                'direction': route.direction,
                'color': route.color,
                'stops': stops_data
            }
        }
        features.append(feature)
    
    return JsonResponse({
        'type': 'FeatureCollection',
        'features': features
    })
