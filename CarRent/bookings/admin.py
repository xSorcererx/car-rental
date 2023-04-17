from django.contrib import admin

from .models import Booking


class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'booking_start', 'booking_end')
admin.site.register(Booking, BookingAdmin)
