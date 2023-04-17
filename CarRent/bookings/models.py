from cars.models import Car
from django.contrib.auth.models import User
from django.db import models


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    booking_start = models.DateField()
    booking_end = models.DateField()
    booking_duration = models.DecimalField(max_digits=3, decimal_places=0)
    created = models.DateTimeField(auto_now_add=True) 
    updated = models.DateTimeField(auto_now=True) 
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-created']
        
    def save(self, *args, **kwargs):
        self.booking_duration = (self.booking_end - self.booking_start).days
        self.total_price = self.booking_duration * self.car.day_price
        super(Booking, self).save(*args, **kwargs)
