from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.


class Driver(models.Model):
    models.AutoField
    name = models.CharField(max_length=20)
    vtype = models.CharField(max_length=20)
    plateNumber = models.CharField(max_length=10)
    numberOfPassagers = models.IntegerField()
    specialInfo = models.CharField(max_length=100)


class Userinfo(models.Model):
    models.AutoField
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    driverStatus = models.BooleanField()


class Ride(models.Model):
    models.AutoField
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=40)
    arrivalTime = models.DateTimeField()
    numberOfPassagers = models.IntegerField()
    type = models.CharField(max_length=20)
    status = models.BooleanField()
    share = models.BooleanField()
    shareNum = models.IntegerField()
    driver = models.CharField(max_length=20)
    creator = models.CharField(max_length=20)
    sharer = models.ForeignKey(Userinfo, on_delete=models.CASCADE, null=True)
    sepReq = models.CharField(max_length=100)
    leftnop = models.IntegerField()
    
class ShareRide(models.Model):
    models.AutoField
    rideid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    nop = models.IntegerField()
    creator = models.CharField(max_length=20)


