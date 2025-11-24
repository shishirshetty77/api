from django.contrib.gis.db import models

class FuelStation(models.Model):
    opis_id = models.IntegerField(unique=True, verbose_name="OPIS Truckstop ID")
    name = models.CharField(max_length=255, verbose_name="Truckstop Name")
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    rack_id = models.IntegerField(verbose_name="Rack ID")
    retail_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Retail Price")
    location = models.PointField(geography=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.city}, {self.state})"

    class Meta:
        indexes = [
            models.Index(fields=['retail_price']),
        ]
