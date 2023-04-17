from django.shortcuts import render
from rest_framework.filters import OrderingFilter
# from rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Booking
from .serializers import BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    User have CRUD operations on own objects.
    Staff have CRUD operation on all objects.
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['car', 'booking_start', 'booking_end', 'created']
    ordering_fields = ['booking_start', 'booking_end']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        else:
            return Booking.objects.filter(user=user)