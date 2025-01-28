from django.core.management.base import BaseCommand
from transit.models import Route, Stop, RouteStop

class Command(BaseCommand):
    help = 'Link routes to stops using the stops_list field'

    def handle(self, *args, **options):
        routes = Route.objects.all()
        total_links = 0
        
        for route in routes:
            if not route.stops_list:
                continue
                
            # Split the stops list and filter out empty strings
            stop_codes = [code.strip() for code in route.stops_list.split(',') if code.strip()]
            
            # Create RouteStop entries
            for sequence, code in enumerate(stop_codes, start=1):
                try:
                    # Try different formats of the stop code
                    stop = None
                    codes_to_try = [
                        code,  # Original code
                        code.lstrip('0'),  # Remove leading zeros
                        str(int(code)) if code.isdigit() else code,  # Convert to int and back to remove leading zeros
                    ]
                    
                    for try_code in codes_to_try:
                        try:
                            stop = Stop.objects.get(code=try_code)
                            break
                        except Stop.DoesNotExist:
                            continue
                    
                    if stop:
                        RouteStop.objects.get_or_create(
                            route=route,
                            stop=stop,
                            sequence=sequence
                        )
                        total_links += 1
                        
                        if total_links % 1000 == 0:
                            self.stdout.write(f"Created {total_links} links...")
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"Stop with code {code} not found for route {route.route_id}"
                        ))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Error linking stop {code} to route {route.route_id}: {str(e)}"
                    ))
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {total_links} route-stop links'
        ))
