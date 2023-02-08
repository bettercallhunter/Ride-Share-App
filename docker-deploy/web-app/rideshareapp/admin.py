from django.contrib import admin
from .models import *


class DriverAdmin(admin.ModelAdmin):
    fields = ['name', 'vtype', 'plateNumber',
              'numberOfPassagers', 'specialInfo']


class RideAdmin(admin.ModelAdmin):
    fields = ['name', 'address', 'arrivalTime',
              'numberOfPassagers', 'type', 'status', 'share', 'shareNum',
              'creator', 'id', "driver", "sharer", "sepReq", 'leftnop',]


class UserinfoAdmin(admin.ModelAdmin):
    fields = ['name', 'email', 'driverStatus']


class ShareRideAdmin(admin.ModelAdmin):
    fields = ['rideid', 'name', 'nop', 'creator',]


admin.site.register(Driver, DriverAdmin)
admin.site.register(Ride, RideAdmin)
admin.site.register(Userinfo, UserinfoAdmin)
admin.site.register(ShareRide, ShareRideAdmin)

# Register your models here.
