from django.core.management.base import BaseCommand
import csv
from transit.models import Stop
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    help = 'Import stops from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to stops.csv')

    def handle(self, *args, **options):
        path = options['csv_path']
        count = 0
        errors = 0
        
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                try:
                    # Convert numeric values with locale handling
                    lat = float(row['lat'].replace(',', '.'))
                    lon = float(row['lon'].replace(',', '.'))
                    
                    Stop.objects.update_or_create(
                        code=row['code'],
                        defaults={
                            'description': row['description'],
                            'description_el': row['description[el]'],
                            'description_en': row['description[en]'],
                            'location': Point(lon, lat)  # Note: longitude first
                        }
                    )
                    count += 1
                except (ValueError, KeyError) as e:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping row {row}: {str(e)}"
                    ))
                    errors += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed {count} stops ({errors} errors)'
        ))