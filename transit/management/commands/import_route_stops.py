import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from transit.models import Route, Stop, RouteStop
from django.contrib.gis.geos import Point
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import route-stop associations from GTFS feed'

    def add_arguments(self, parser):
        parser.add_argument('gtfs_dir', type=str, help='Path to GTFS directory')

    def handle(self, *args, **options):
        gtfs_dir = Path(options['gtfs_dir'])
        
        # Ensure required files exist
        required_files = ['stops.txt', 'routes.txt', 'stop_times.txt', 'trips.txt']
        for file in required_files:
            if not (gtfs_dir / file).exists():
                self.stderr.write(self.style.ERROR(f'Required file {file} not found in {gtfs_dir}'))
                return

        try:
            with transaction.atomic():
                # Clear existing route-stop associations
                RouteStop.objects.all().delete()
                
                # Load trips to get route associations
                trips_by_route = {}
                with open(gtfs_dir / 'trips.txt', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        trips_by_route[row['trip_id']] = row['route_id']
                
                # Load stop times and build route-stop associations
                stop_sequences = {}  # (route_id, stop_id) -> set of sequences
                with open(gtfs_dir / 'stop_times.txt', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        trip_id = row['trip_id']
                        route_id = trips_by_route.get(trip_id)
                        if route_id:
                            key = (route_id, row['stop_id'])
                            if key not in stop_sequences:
                                stop_sequences[key] = set()
                            stop_sequences[key].add(int(row['stop_sequence']))

                # Create RouteStop entries
                route_stops = []
                routes = {route.route_id: route for route in Route.objects.all()}
                stops = {stop.code: stop for stop in Stop.objects.all()}

                for (route_id, stop_id), sequences in stop_sequences.items():
                    route = routes.get(route_id)
                    stop = stops.get(stop_id)
                    if route and stop:
                        # Use the minimum sequence number for this stop on this route
                        sequence = min(sequences)
                        route_stops.append(RouteStop(
                            route=route,
                            stop=stop,
                            sequence=sequence
                        ))

                # Bulk create route-stop associations
                if route_stops:
                    RouteStop.objects.bulk_create(route_stops)
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully imported {len(route_stops)} route-stop associations'
                    ))
                else:
                    self.stdout.write(self.style.WARNING('No route-stop associations found to import'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error importing route-stop associations: {str(e)}'))
            logger.exception('Error importing route-stop associations')
            raise
