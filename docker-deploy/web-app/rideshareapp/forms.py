from django.forms import ModelForm
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


class DriverForm(ModelForm):
    name = forms.CharField(max_length=20)
    vtype = forms.CharField(max_length=20)
    plateNumber = forms.CharField(max_length=10)
    numberOfPassagers = forms.IntegerField()
    specialInfo = forms.CharField(max_length=100)

    class Meta:
        model = Driver
        fields = '__all__'


class RideForm(ModelForm):
    name = forms.CharField(max_length=20)
    address = forms.CharField(max_length=40)
    arrivalTime = forms.DateTimeField()
    numberOfPassagers = forms.IntegerField()
    type = forms.CharField(max_length=20)

    class Meta:
        model = Ride
        fields = '__all__'


class RegisterForm(UserCreationForm):
    # email = forms.EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email") # , 'password1', 'password2')
