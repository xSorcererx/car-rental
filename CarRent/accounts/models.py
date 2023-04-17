from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    apartment_number = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    
    def __str__(self):
        return self.user.username
