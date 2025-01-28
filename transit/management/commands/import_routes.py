import os
from django.core.management.base import BaseCommand
from django.contrib.gis.gdal import DataSource
from transit.models import Route
from django.utils import timezone
import re

class Command(BaseCommand):
    help = 'Import routes from Shapefile'

    def add_arguments(self, parser):
        parser.add_argument('shp_dir', type=str, help='Directory containing routes.shp')

    def parse_time(self, time_str):
        try:
            return timezone.datetime.strptime(time_str, '%H:%M').time()
        except:
            return None

    def parse_float(self, value):
        try:
            return float(str(value).replace(',', '.'))
        except (ValueError, TypeError):
            return None

    def generate_color(self, LINE_NAME_):
        base_hash = hash(LINE_NAME_) % 0xFFFFFF
        return f"#{base_hash:06x}"

    def handle(self, *args, **options):
        shp_path = os.path.join(options['shp_dir'], 'routes.shp')
        
        if not os.path.exists(shp_path):
            self.stdout.write(self.style.ERROR(f'Shapefile not found: {shp_path}'))
            return

        ds = DataSource(shp_path)
        layer = ds[0]
        
        created_count = 0
        for feature in layer:
            try:
                # Use LINE_NAME_ as route_id since ID is empty
                route_id = feature['LINE_NAME_'].value
                if not route_id:
                    self.stdout.write(self.style.WARNING(f"Skipping feature with empty LINE_NAME_"))
                    skipped_count += 1
                    continue

                route_data = {
                    'route_id': route_id,
                    #'line_name': feature['LINE_NAME_'].value,
                    #'route_name': feature['ROUTE_NAME'].value,
                    #'direction': feature['DIRECTION'].value,
                    #'length': self.parse_float(feature['LINE_LENGT'].value),
                    #'first_stop': feature['FIRST_STOP'].value,
                    #'last_stop': feature['LAST_STOP_'].value,
                    #'stops_list': feature['STOPS'].value,
                    #'geometry': feature.geom.wkt,
                    'color': self.generate_color(route_id),
                    #'weekday_start': self.parse_time(feature['WD_START_H'].value),
                    #'weekday_end': self.parse_time(feature['WD_LAST_HO'].value),
                    #'saturday_start': self.parse_time(feature['SAT_START_'].value),
                    #'saturday_end': self.parse_time(feature['SAT_LAST_H'].value),
                    #'holiday_start': self.parse_time(feature['HOL_START_'].value),
                    #'holiday_end': self.parse_time(feature['HOL_LAST_H'].value),
                }

                Route.objects.update_or_create(
                    route_id=route_data['route_id'],
                    defaults=route_data
                )
                created_count += 1

            except KeyError as e:
                self.stdout.write(self.style.ERROR(
                    f"Missing field {str(e)} in feature {feature['ID'].value}"
                ))
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f"Skipping route {route_data['route_id']}: {str(e)}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully imported/updated {created_count} routes'
        ))

        # Add debug output
        self.stdout.write(f"Shapefile fields: {layer.fields}") 