from django.core.management.base import BaseCommand
from django.core.cache import cache
from .services import fetch_and_store_realtime_data

class Command(BaseCommand):
    help = 'Fetches realtime transit data from GTFS-RT feed'

    def handle(self, *args, **options):
        fetch_and_store_realtime_data()
        cache.delete('realtime_positions')  # Invalidate cache
        self.stdout.write('Successfully updated realtime vehicle positions') 