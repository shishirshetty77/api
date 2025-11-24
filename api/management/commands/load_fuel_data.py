import csv
import time
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from api.models import FuelStation

class Command(BaseCommand):
    help = 'Load fuel prices from CSV and geocode addresses'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument('--limit', type=int, default=None, help='Limit number of records to process')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        limit = options['limit']
        
        geolocator = Nominatim(user_agent="fuel_project_loader")
        
        with open(csv_file_path, 'r') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                if limit and count >= limit:
                    break
                
                opis_id = int(row['OPIS Truckstop ID'])
                
                if FuelStation.objects.filter(opis_id=opis_id).exists():
                    self.stdout.write(self.style.WARNING(f"Station {opis_id} already exists. Skipping."))
                    continue

                address_str = f"{row['Address']}, {row['City']}, {row['State']}, USA"
                
                location = None
                try:
                    # Geocode
                    # self.stdout.write(f"Geocoding: {address_str}")
                    geo = geolocator.geocode(address_str, timeout=10)
                    if geo:
                        location = Point(geo.longitude, geo.latitude)
                    else:
                        self.stdout.write(self.style.ERROR(f"Could not geocode: {address_str}"))
                    
                    # Respect rate limit
                    time.sleep(1.1) 
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error geocoding {address_str}: {e}"))

                FuelStation.objects.create(
                    opis_id=opis_id,
                    name=row['Truckstop Name'],
                    address=row['Address'],
                    city=row['City'],
                    state=row['State'],
                    rack_id=int(row['Rack ID']),
                    retail_price=row['Retail Price'],
                    location=location
                )
                
                count += 1
                if count % 10 == 0:
                    self.stdout.write(self.style.SUCCESS(f"Processed {count} stations..."))

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {count} stations"))
