from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from PIL import Image


class Car(models.Model):
    CONDITION = (
        ("used", "used"),
        ("new", "new"),
    )

    brand = models.CharField(max_length=40)
    model = models.CharField(max_length=50)
    engine = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    mileage = models.DecimalField(max_digits=6, decimal_places=0)
    location = models.CharField(max_length=50)
    condition = models.CharField(max_length=50, choices=CONDITION)
    day_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return "{} {}".format(self.brand, self.model)


class CarPhoto(models.Model):
    car = models.ForeignKey(Car, related_name="photos", on_delete=models.CASCADE)
    photo = models.ImageField(blank=True, null=True, upload_to="photos")
           
