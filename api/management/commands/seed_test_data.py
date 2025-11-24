from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from api.models import FuelStation
import random

class Command(BaseCommand):
    help = 'Seed database with test fuel stations along I-95 (NY to DC)'

    def handle(self, *args, **options):
        stations = [
            # NY
            {"name": "Jersey City Fuel", "city": "Jersey City", "state": "NJ", "lat": 40.7282, "lon": -74.0776, "price": 3.10},
            {"name": "Newark Airport Gas", "city": "Newark", "state": "NJ", "lat": 40.6895, "lon": -74.1745, "price": 3.05},
            # NJ Turnpike
            {"name": "Joyce Kilmer Service Area", "city": "East Brunswick", "state": "NJ", "lat": 40.4185, "lon": -74.4167, "price": 3.25},
            {"name": "Walt Whitman Service Area", "city": "Cherry Hill", "state": "NJ", "lat": 39.9283, "lon": -75.0064, "price": 3.30},
            # Delaware
            {"name": "Delaware House", "city": "Newark", "state": "DE", "lat": 39.6631, "lon": -75.6928, "price": 2.99},
            # Maryland
            {"name": "Maryland House", "city": "Aberdeen", "state": "MD", "lat": 39.4987, "lon": -76.2097, "price": 3.15},
            {"name": "Chesapeake House", "city": "North East", "state": "MD", "lat": 39.6178, "lon": -76.0333, "price": 3.12},
            # DC Area
            {"name": "College Park Gas", "city": "College Park", "state": "MD", "lat": 39.0000, "lon": -76.9300, "price": 3.40},
        ]

        count = 0
        for i, s in enumerate(stations):
            opis_id = 9000 + i # Fake ID
            if not FuelStation.objects.filter(opis_id=opis_id).exists():
                FuelStation.objects.create(
                    opis_id=opis_id,
                    name=s['name'],
                    address="I-95",
                    city=s['city'],
                    state=s['state'],
                    rack_id=100,
                    retail_price=s['price'],
                    location=Point(s['lon'], s['lat'])
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Seeded {count} test stations along I-95"))
