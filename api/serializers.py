from rest_framework import serializers
from .models import FuelStation

class RouteRequestSerializer(serializers.Serializer):
    start_location = serializers.CharField(max_length=255, help_text="Start location (e.g. 'New York, NY')")
    finish_location = serializers.CharField(max_length=255, help_text="Finish location (e.g. 'Los Angeles, CA')")

class FuelStopSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = FuelStation
        fields = ['opis_id', 'name', 'address', 'city', 'state', 'retail_price', 'latitude', 'longitude']

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None

class RouteResponseSerializer(serializers.Serializer):
    route_geometry = serializers.JSONField(help_text="GeoJSON LineString of the route")
    stops = FuelStopSerializer(many=True)
    total_fuel_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_distance_miles = serializers.FloatField()
    map_url = serializers.URLField(required=False, allow_null=True)
