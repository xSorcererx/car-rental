from datetime import date, datetime

from cars.models import Car
from cars.serializers import CarSerializer
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Booking


class BookingSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for booking that serialize 'url', 'user', 
    'booking_start', 'booking_end', 'created', 'updated', 
    'booking_duration', 'total_price'
    and relation to car serializer
    """
    url = serializers.HyperlinkedIdentityField(view_name="bookings-detail")
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, 
        default=serializers.CurrentUserDefault())
    
    # Nested CarSerializer on read
    car = CarSerializer(read_only=True)
    
    # CarField on write
    car_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='car',
        queryset=Car.objects.all(),
        label='Car')
           
    class Meta:
        model = Booking
        fields = ['url', 'user', 'car', 'car_id', 'booking_start', 
                  'booking_end', 'created', 'updated', 'booking_duration',
                  'total_price']
        extra_kwargs = {
            'booking_duration': {'read_only':True},
            'total_price': {'read_only':True}
        }
                
    def validate(self, data):
        """
        Ensures that user can not book a car this is already booked
        in selected period
        """
        booking_start = data.get('booking_start')
        booking_end = data.get('booking_end')
        car = data.get('car')
        instance = self.instance
        
        # Requested booking ends during existing booking, 
        # select sooner booking end date
        case_1 = Booking.objects.filter(car=car,
                                        booking_start__lte=booking_start,
                                        booking_end__gte=booking_start
        ).exists()
        # Requested booking starts during existing booking,
        # select later booking start date
        case_2 = Booking.objects.filter(car=car,
                                        booking_start__lte=booking_end,
                                        booking_end__gte=booking_end
        ).exists()
        # Requested booking starts and ends during existing booking
        case_3 = Booking.objects.filter(car=car,
                                        booking_start__gte=booking_start,
                                        booking_end__lte=booking_end
        ).exists()
        
        if not (instance and instance.car == car):
            if case_1:
                raise ValidationError(
                    """Requested booking ends during existing booking, \
                    select sooner booking end date"""
                    )
            elif case_2:
                raise ValidationError(
                    "Requested booking starts during existing booking, \
                        select later booking start date"
                    )
            elif case_3:
                raise ValidationError(
                    'Requested booking starts and ends during existing booking'
                    )
            return data
        return data
        
    def validate_booking_start(self, value):
        """
        Ensures that the earlies possible booking start day is today
        """
        booking_start = value
        today_value = timezone.now().today().date()
        if booking_start < today_value:
            raise ValidationError(
                f'Booking start date must be greater than {today_value}'
                )
        return super(BookingSerializer, self).validate(value)
    
    def validate_booking_end(self, value):
        """
        Ensures that booking end date can not be before booking start date
        """
        data = self.get_initial()
        booking_start = data.get('booking_start')
        booking_start = datetime.strptime(booking_start, '%Y-%m-%d').date()
        booking_end = value
        if booking_end < booking_start:
            raise ValidationError(
                'Booking end date must be greater than booking start date'
                )
        return super(BookingSerializer, self).validate(value)
            
    def save(self, **kwargs):
        """
        Include default for read_only `user` field
        """
        kwargs["user"] = self.fields["user"].get_default()
        return super().save(**kwargs)
    