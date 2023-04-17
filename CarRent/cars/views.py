from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Car, CarPhoto
from .permissions import IsAdminUserOrReadOnly
from .serializers import CarPhotoSerializer, CarSerializer


class CarViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions for staff
    and 'list' , 'retrieve' for any user.
    """
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    

class CarPhotoViewSet(viewsets.ModelViewSet):    
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions for staff
    """
    queryset = CarPhoto.objects.all()
    serializer_class = CarPhotoSerializer
    permission_classes = [IsAdminUser]