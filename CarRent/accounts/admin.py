from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'country', 'city',
                    'postal_code', 'street', 'apartment_number', 'phone_number')
    
admin.site.register(Profile, ProfileAdmin)