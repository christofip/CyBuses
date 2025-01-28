from django.utils import timezone
from transit.models import VehiclePosition
from google.transit import gtfs_realtime_pb2
import requests

def fetch_realtime_data(url):
    """Fetch and parse GTFS-RT data"""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed
        
    except Exception as e:
        raise RuntimeError(f"GTFS-RT fetch failed: {str(e)}")

def process_vehicle_positions(feed):
    """Process feed entities into VehiclePosition objects"""
    positions = []
    for entity in feed.entity:
        if entity.HasField('vehicle'):
            vp = entity.vehicle
            positions.append(
                VehiclePosition(
                    vehicle_id=vp.vehicle.id,
                    license_plate=vp.vehicle.license_plate,
                    latitude=vp.position.latitude,
                    longitude=vp.position.longitude,
                    bearing=vp.position.bearing,
                    speed=vp.position.speed,
                    timestamp=timezone.datetime.fromtimestamp(vp.timestamp),
                    route_id=vp.trip.route_id,
                    trip_id=vp.trip.trip_id
                )
            )
    return positions 