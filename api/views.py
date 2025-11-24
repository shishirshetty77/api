from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import RouteRequestSerializer, RouteResponseSerializer
from .utils import RouteOptimizer

class RouteView(APIView):
    @extend_schema(
        request=RouteRequestSerializer,
        responses={200: RouteResponseSerializer},
        description="Calculate optimal fuel stops for a route between two USA locations."
    )
    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        if serializer.is_valid():
            start = serializer.validated_data['start_location']
            finish = serializer.validated_data['finish_location']
            
            optimizer = RouteOptimizer()
            
            # 1. Geocode
            start_coords = optimizer.get_coordinates(start)
            finish_coords = optimizer.get_coordinates(finish)
            
            if not start_coords or not finish_coords:
                return Response(
                    {"error": "Could not geocode one or both locations."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. Get Route
            geometry, distance_meters = optimizer.get_route(start_coords, finish_coords)
            
            if not geometry:
                return Response(
                    {"error": "Could not find a route."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. Optimize Stops
            stops, fuel_cost, distance_miles = optimizer.find_optimal_stops(geometry, distance_meters)
            
            response_data = {
                "route_geometry": geometry,
                "stops": stops,
                "total_fuel_cost": fuel_cost,
                "total_distance_miles": distance_miles,
                "map_url": None # Could generate a static map URL here
            }
            
            return Response(RouteResponseSerializer(response_data).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
