import requests
from django.contrib.gis.geos import LineString
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import LineLocatePoint
from django.db.models.functions import Cast
from django.contrib.gis.db.models import GeometryField
from geopy.geocoders import Nominatim
from .models import FuelStation

class RouteOptimizer:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="fuel_project_assessment", timeout=10)
        self.osrm_url = "http://router.project-osrm.org/route/v1/driving/"

    def get_coordinates(self, location_name):
        try:
            location = self.geocoder.geocode(location_name + ", USA")
            if location:
                return location.longitude, location.latitude
        except Exception:
            pass
        return None

    def get_route(self, start_coords, finish_coords):
        coords_str = f"{start_coords[0]},{start_coords[1]};{finish_coords[0]},{finish_coords[1]}"
        url = f"{self.osrm_url}{coords_str}?overview=full&geometries=geojson"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 'Ok':
                    route = data['routes'][0]
                    return route['geometry'], route['distance']
        except Exception:
            pass
        return None, 0

    def find_optimal_stops(self, route_geometry, total_distance_meters):
        route_linestring = LineString(route_geometry['coordinates'], srid=4326)
        
        stations = FuelStation.objects.filter(
            location__dwithin=(route_linestring, D(mi=10))
        ).annotate(
            fraction=LineLocatePoint(route_linestring, Cast('location', GeometryField()))
        ).order_by('fraction')

        MAX_RANGE_MILES = 500
        MPG = 10
        total_distance_miles = total_distance_meters / 1609.34
        
        stops = []
        total_cost = 0.0
        current_fuel_miles = MAX_RANGE_MILES
        
        station_list = list(stations)
        last_stop_fraction = 0.0
        
        while True:
            dist_to_finish_miles = (1.0 - last_stop_fraction) * total_distance_miles
            
            if current_fuel_miles >= dist_to_finish_miles:
                break
            
            reachable_stations = []
            for s in station_list:
                dist_from_last = (s.fraction - last_stop_fraction) * total_distance_miles
                if dist_from_last > 0 and dist_from_last <= current_fuel_miles:
                    reachable_stations.append(s)
            
            if not reachable_stations:
                break
                
            best_station = min(reachable_stations, key=lambda s: s.retail_price)
            
            dist_traveled = (best_station.fraction - last_stop_fraction) * total_distance_miles
            current_fuel_miles -= dist_traveled
            
            future_stations = [s for s in station_list if s.fraction > best_station.fraction]
            cheaper_ahead = False
            for fs in future_stations:
                dist_ahead = (fs.fraction - best_station.fraction) * total_distance_miles
                if dist_ahead <= MAX_RANGE_MILES and fs.retail_price < best_station.retail_price:
                    cheaper_ahead = True
                    break
            
            gallons_needed = 0
            if cheaper_ahead:
                added_fuel_miles = MAX_RANGE_MILES - current_fuel_miles
                gallons_needed = added_fuel_miles / MPG
                current_fuel_miles = MAX_RANGE_MILES
            else:
                added_fuel_miles = MAX_RANGE_MILES - current_fuel_miles
                gallons_needed = added_fuel_miles / MPG
                current_fuel_miles = MAX_RANGE_MILES
            
            cost = gallons_needed * float(best_station.retail_price)
            total_cost += cost
            stops.append(best_station)
            
            last_stop_fraction = best_station.fraction
            station_list = [s for s in station_list if s.fraction > last_stop_fraction]

        return stops, total_cost, total_distance_miles
