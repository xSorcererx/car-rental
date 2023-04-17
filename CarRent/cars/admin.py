from django.contrib import admin
from .models import Car, CarPhoto


class CarPhotoInline(admin.StackedInline):
    model = CarPhoto
    
    
class CarAdmin(admin.ModelAdmin):
    inlines = [CarPhotoInline]


admin.site.register(Car, CarAdmin)