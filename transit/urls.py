from django.urls import path
from .views import MapView, realtime_positions, get_stops_json, routes_geojson
from transit.views import RealtimeVehicleView

app_name = 'transit'

urlpatterns = [
    path('realtime/', RealtimeVehicleView.as_view(), name='realtime-vehicles'),
    path('realtime/positions/', realtime_positions, name='realtime-positions'),
    path('', MapView.as_view(), name='map'),
    path('stops.json', get_stops_json, name='stops-json'),
    path('routes.geojson', routes_geojson, name='routes-geojson'),
] 