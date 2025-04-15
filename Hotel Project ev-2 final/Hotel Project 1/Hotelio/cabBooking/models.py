from django.db import models

from django.db import models

class CarBooking(models.Model):
    car_name = models.CharField(max_length=100)
    car_price = models.DecimalField(max_digits=10, decimal_places=2)  # Rate per hour

    # Booking details
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255,default=-1)

    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    dropoff_date = models.DateField()
    dropoff_time = models.TimeField()

    # User info
    username = models.CharField(max_length=100,default=-1)

    phone = models.CharField(max_length=20,default=-1)

    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car_name} - {self.pickup_location} to {self.dropoff_location} ({self.pickup_date})"

    
class TaxiCar(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='car_images/')
    rate_per_hour = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name
