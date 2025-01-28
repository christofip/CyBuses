from django.core.management.base import BaseCommand
from transit.models import RealtimeVehicle
import requests
from google.transit import gtfs_realtime_pb2
from django.utils import timezone
from django.db import transaction
from transit.services import fetch_realtime_data, process_vehicle_positions

class Command(BaseCommand):
    help = 'Fetches and processes real-time vehicle positions'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, help='GTFS-RT endpoint URL')

    def handle(self, *args, **options):
        url = options.get('url') or "https://api.example.com/gtfs-rt/vehiclepositions"
        
        try:
            # Fetch feed
            self.stdout.write(f"Fetching data from {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse feed
            feed = fetch_realtime_data(url)
            positions = process_vehicle_positions(feed)
            self.stdout.write(f"Received {len(positions)} entities")
            
            # Process entities
            with transaction.atomic():
                RealtimeVehicle.objects.all().delete()
                
                created_count = 0
                for position in positions:
                    try:
                        RealtimeVehicle.objects.create(
                            vehicle_id=position.vehicle_id,
                            license_plate=position.license_plate,
                            latitude=position.latitude,
                            longitude=position.longitude,
                            bearing=position.bearing,
                            speed=position.speed,
                            timestamp=position.timestamp,
                            route_id=position.route_id,
                            trip_id=position.trip_id,
                            current_status='IN_TRANSIT',  # Default status
                            current_stop_sequence=0  # Default sequence
                        )
                        created_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping position {position.id}: {str(e)}"
                        ))
                            
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully stored {created_count}/{len(positions)} vehicle positions"
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
