from rest_framework import serializers

from .models import Car, CarPhoto


class CarPhotoSerializer(serializers.HyperlinkedModelSerializer):
    """
    serializer to enable nesting in car serializer
    """
    class Meta:
        model = CarPhoto
        fields = ['url', 'car', 'photo']
        extra_kwargs = {
            'car': {'write_only': True},
        }


class CarSerializer(serializers.HyperlinkedModelSerializer):
    """
    serialzier for car that serialize 'url', 'brand', 'model', 'engine', 
    'year', 'location', 'condition', 'day_price' 
    and relation to car photo serializer
    """
    photos = CarPhotoSerializer(many=True, read_only=True)
        
    class Meta:
        model = Car
        fields = ['url', 'brand', 'model', 'engine', 'year', 'location', 
                  'condition', 'day_price', 'photos']
        
