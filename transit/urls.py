from django.urls import path
from .views import MapView, realtime_positions, get_stops_json, routes_geojson

app_name = 'transit'

urlpatterns = [
    path('realtime/positions/', realtime_positions, name='realtime-positions'),
    path('', MapView.as_view(), name='map'),
    path('stops.json', get_stops_json, name='stops-json'),
    path('routes.geojson', routes_geojson, name='routes-geojson'),
]