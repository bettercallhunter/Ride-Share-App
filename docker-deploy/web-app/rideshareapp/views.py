from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import *
import uuid
import django.contrib.auth.password_validation as validators
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
# Create your views here.


def login(request):
    if request.method == "POST":

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user:
                auth_login(request, user)
                return redirect(home)
        else:
            messages.error(request, "wrong password or username")
            return redirect(login)
    else:
        return render(request, 'rideshare/login.html')


@login_required
def home(request):
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus
    return render(request, 'rideshare/home.html', {'isdriver': isdriver})


@login_required
def logout(request):
    auth_logout(request)
    return redirect(login)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        isexist = User.objects.filter(username=request.POST['username'])
        if (isexist):
            messages.error(request, 'Username already exists')
            return render(request, 'rideshare/signup.html')
        elif (request.POST['password1'] != request.POST['password2']):
            messages.error(
                request, 'password confirmation doesn\'t match please try again')
            return render(request, 'rideshare/signup.html')

        if form.is_valid():
            # user = form.save()
            # suusername = form.cleaned_data.get('username')
            # supassword1 = form.cleaned_data.get('password1')
            # supassword2 = form.cleaned_data.get('password2')
            # suemail = form.cleaned_data.get('suemail')
            suusername = request.POST['username']
            supassword = request.POST['password1']
            suemail = request.POST['suemail']

            Userinfo.objects.create(
                name=suusername, email=suemail, driverStatus=False)
            user = User.objects.create_user(
                username=suusername, password=supassword, email=suemail)
            user.save()
            messages.success(
                request, "Registration Successed. Please Sign In.")
            return redirect(success)
        else:
            form = UserCreationForm()
            messages.error(
                request, 'This password is too short. It must contain at least 8 characters.')
            messages.error(request, 'This password is too common.')
            messages.error(
                request, 'This password is entirely numeric.')

            return render(request, 'rideshare/signup.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'rideshare/signup.html', {'form': form})


# @login_required
def success(request):
    return render(request, 'rideshare/success.html')


@login_required
def rideowner(request):

        
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus
    ride_list = Ride.objects.filter(creator=request.user.username,status=True)
    # sharer_list = Ride.objects.select_related('sharer').all()
    
   
  
    return render(request, 'rideshare/rideowner.html', {'ride_list': ride_list, 'isdriver': isdriver})


@login_required
def createride(request):
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus
    if request.method == "POST":
        type = request.POST['type']
        name = request.POST['name']
        address = request.POST['address']
        arrivalTime = request.POST['arrivalTime']
        numberOfPassagers = request.POST['numberOfPassagers']
        sepReq = request.POST['spReq']
        isshare = False
        if request.POST['isshare'] == 'True':
            isshare = True
        currRide = Ride.objects.last()
        if currRide:
            rideid = currRide.id+1
        else:
            rideid = 1
        Ride.objects.create(name=name, type=type, address=address,
                            numberOfPassagers=numberOfPassagers, arrivalTime=arrivalTime,
                            status=True, share=isshare, shareNum=0, creator=request.user.username,
                            id=rideid, driver='', leftnop=numberOfPassagers, sepReq=sepReq)
        messages.success(request, "submission succeed")
        return redirect(rideowner)
    else:
        form = RideForm()
    return render(request, 'rideshare/newride.html', {'isdriver': isdriver})


@login_required
def confirm(request, id):
    ride = Ride.objects.get(id=id)
    ride.driver = request.user.username

    rideCreatorInfo = Userinfo.objects.get(name=ride.creator)

    driver = Driver.objects.get(name=request.user.username)
    ride.leftnop += ride.numberOfPassagers
    ride.save()

    mesC = 'Your ride have been accepted by your driver ' + driver.name
    mesD = 'You confirm a ride from ' + ride.creator
    messageC = ('Your Ride Has Been Accepted', mesC, settings.EMAIL_HOST_USER, [rideCreatorInfo.email])
    messageD = ('You Confirm a Ride', mesD, settings.EMAIL_HOST_USER, [request.user.email])
    send_mass_mail((messageC, messageD), fail_silently=False)

    return redirect(ridedriver)


@login_required
def ridesharer(request):
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus
    user = Userinfo.objects.filter(name=request.user.username)
    ride_list = Ride.objects.filter(
        status=True, sharer__in=user)
    return render(request, 'rideshare/ridesharer.html', {'ride_list': ride_list, 'isdriver': isdriver})

@login_required
def cancelridesharer(request, rideid):
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus
    ride = Ride.objects.get(id=rideid)
    user = Userinfo.objects.get(name=request.user.username)
    ride.sharer.remove(user)

    send_mail(
        subject='Cancel Share',
        message='You canceled your share ride.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[Userinfo.objects.get(name=request.user.username).email],
        fail_silently=False
    )
    send_mail(
        subject='Cancel Share',
        message='The Sharer canceled sharing.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[Userinfo.objects.get(name=ride.creator).email],
        fail_silently=False
    )

    return redirect(ridesharer)


@login_required
def ridedriver(request):
    ride_list = Ride.objects.filter(driver=request.user.username, arrivalTime__gte=timezone.now(), status=True)
    sharer_list = Ride.objects.filter(driver=request.user.username, arrivalTime__gte=timezone.now(), status=True).select_related('sharer')
    if not ride_list:
        dloCheck = True
    else:
        dloCheck = False

    if request.method == "POST":
        duserinfo = Userinfo.objects.get(name=request.user.username)
        duserinfo.driverStatus = False
        duserinfo.save()
        Driver.objects.get(name=request.user.username).delete()
        messages.success(request, "now you are not a driver")
        send_mail(
            subject='Logout Driver',
            message='You have logouted driver. Thank you for using.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[Userinfo.objects.get(name=request.user.username).email],
            fail_silently=False
        )
        return redirect(home)

    return render(request, 'rideshare/ridedriver.html', {'ride_list': ride_list, 'dloCheck': dloCheck,'sharer_list':sharer_list})


@login_required
def driversearchride(request):
    user= Userinfo.objects.filter(name=request.user.username)
    driver = Driver.objects.get(name=request.user.username)
    ride_list = Ride.objects.filter(~Q(sharer =None),~Q(sharer__in=user),
        numberOfPassagers__lte=driver.numberOfPassagers, arrivalTime__gte=timezone.now(), driver='',status=True)

    re_list = {'ride_list': ride_list,
               'dname': request.user.username,
               'vtype': driver.vtype,
               'nop': driver.numberOfPassagers,
               'speReq': driver.specialInfo}

    return render(request, 'rideshare/driversearchride.html', re_list, )


# @login_required
# def getDriver(request):

#     return


@login_required
def registerdriver(request):
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus
    if request.method == "POST":
        name = request.user.username
        # form = DriverForm(request.POST)
        # if form.is_valid():
        vtype = request.POST['vtype']
        plateNumber = request.POST['plateNumber']
        numberOfPassagers = request.POST['numberOfPassagers']
        spInfo = request.POST['specialInfo']
        Driver.objects.create(name=name, vtype=vtype, plateNumber=plateNumber,
                              numberOfPassagers=numberOfPassagers, specialInfo=spInfo)
        user = Userinfo.objects.get(name=request.user.username)
        user.driverStatus = True
        user.save()

        messages.success(request, "submission succeed")
        send_mail(
            subject='Become a Driver',
            message='Congratulations! Now you have become a driver.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[Userinfo.objects.get(name=request.user.username).email],
            fail_silently=False
        )

        return redirect(ridedriver)

        # else:
        #     messages.error(request, form)

    return render(request, 'rideshare/registerdriver.html', {'name': request.user.username, 'isdriver': isdriver})


@login_required
def editride(request, rideid):
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus
    ride = Ride.objects.get(id=rideid, driver='')
    if request.method == "POST":
        ride.type = request.POST['type']
        ride.name = request.POST['name']
        ride.address = request.POST['address']
        ride.arrivalTime = request.POST['arrivalTime']
        ride.numberOfPassagers = request.POST['numberOfPassagers']
        ride.sepReq = request.POST['spReq']
        ride.save()

        messages.success(request, "submission succeed")
        return redirect(rideowner)
    # else:
    #     form = RideForm()
    oform = {'name': ride.name,
             'type': ride.type,
             'addr': ride.address,
             'arrTime': ride.arrivalTime,
             'nop': ride.numberOfPassagers,
             'sepReq': ride.sepReq,
             'isdriver': isdriver, }
    return render(request, 'rideshare/editride.html', oform)


@login_required
def deleteride(request, rideid):
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus
    Ride.objects.filter(id=rideid).delete()
    # if Ride.driver:
    #     driver = Driver.objects.get(name=Ride.driver)
    #     driver.numberOfPassagers += Ride.numberOfPassagers
    #     driver.save()

    send_mail(
        subject='Delete Ride',
        message='You have deleted your ride',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[Userinfo.objects.get(name=request.user.username).email],
        fail_silently=False
    )

    return redirect(rideowner)


@login_required
def cancelride(request, rideid):
    ride = Ride.objects.get(id=rideid)
    ride.driver = ''
    ride.save()
    # driver = Driver.objects.get(name=request.user.username)
    # driver.numberOfPassagers += ride.numberOfPassagers

    mesC = 'Your driver have been canceled your ride. Please wait for a new driver.'
    mesD = 'You have canceled ' + ride.creator + '\'s ride.'
    messageC = ('Your Ride Has Been Accepted', mesC, settings.EMAIL_HOST_USER, [Userinfo.objects.get(name=ride.creator).email])
    messageD = ('You Confirm a Ride', mesD, settings.EMAIL_HOST_USER, [request.user.email])
    send_mass_mail((messageC, messageD), fail_silently=False)

    return redirect(ridedriver)


@login_required
def profile(request):
    # if (Userinfo.objects.get(name=request.user.username).driverStatus):
    #     isDriver = 'Yes'
    # else:
    #     isDriver = 'No'
    isDriver = Userinfo.objects.get(name=request.user.username).driverStatus

    if request.method == "POST":
        oldpw = request.POST['opw']
        newpw = request.POST['npw']
        newpwc = request.POST['cnpw']
        user = authenticate(
            request, username=request.user.username, password=oldpw)

        if user:
            if newpw == newpwc:
                if newpw == oldpw:
                    messages.error(
                        request, "the same password as the old one please change")
                    return render(request, 'rideshare/profile.html', {'username': request.user.username, 'email': request.user.email, 'isdriver': isDriver},)

                errors = dict()
                try:
                    valid = validators.validate_password(
                        password=newpw, user=request.user.username)
                except validators.ValidationError as e:
                    errors['massages'] = list(e.messages)

                if errors:
                    messages.error(
                        request, 'This password is too short. It must contain at least 8 characters.')
                    messages.error(request, 'This password is too common.')
                    messages.error(
                        request, 'This password is entirely numeric.')

                    return render(request, 'rideshare/profile.html', {'username': request.user.username, 'email': request.user.email, 'isdriver': isDriver},)

                u = User.objects.get(username=request.user.username)
                u.set_password(newpw)
                u.save()

                validators.password_changed(
                    password=newpw, user=request.user.username)
                messages.success(request, "Password Change Success")
                # return render(request, 'rideshare/profile.html', {'username': request.user.username, 'email': request.user.email, 'isdriver': isDriver},)
                return redirect(login)
            else:
                messages.error(
                    request, "password confirmation doesn't match please try again")
                return render(request, 'rideshare/profile.html', {'username': request.user.username, 'email': request.user.email, 'isdriver': isDriver},)
        else:
            messages.error(request, "wrong password please check old password")
            return render(request, 'rideshare/profile.html', {'username': request.user.username, 'email': request.user.email, 'isdriver': isDriver},)

    else:
        return render(request, 'rideshare/profile.html', {'username': request.user.username, 'email': request.user.email, 'isdriver': isDriver},)


@login_required
def searchridesharer(request):
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus

    user = Userinfo.objects.filter(name=request.user.username)
    if request.method == "POST":
        arrivaltime = request.POST['arrivalTime']
        address = request.POST['address']
        numberOfPassagers = request.POST['numberOfPassagers']
        spReq = request.POST['spReq']
        ride_list = Ride.objects.filter(
            leftnop__gte=numberOfPassagers, address=address, sepReq=spReq, arrivalTime__gte=timezone.now(), arrivalTime__lte=arrivaltime,status =True).exclude(sharer__in=user)
        return render(request, 'rideshare/shareshowride.html', {'ride_list': ride_list, 'snop': numberOfPassagers, 'spReq': spReq})
    return render(request, 'rideshare/sharersearchride.html', {'isdriver': isdriver})


@login_required
def joinride(request, rideid):
    isdriver = Userinfo.objects.get(name=request.user.username).driverStatus
    ride = Ride.objects.get(id=rideid)
    user = Userinfo.objects.get(name=request.user.username)
    ride.sharer.add(user)
    snop = request.GET['snop']
    ride.leftnop += int(snop)
    ride.save()
    
    ShareRide.objects.create(rideid=rideid, name=request.user.username, nop=snop, creator=request.user.username)

    mesC = request.user.username + ' joined into your ride.'
    mesS = 'You have joined into ' + ride.creator + '\'s ride.'
    messageC = ('Your Ride Has a Sharer', mesC, settings.EMAIL_HOST_USER, [Userinfo.objects.get(name=ride.creator).email])
    messageS = ('You Join a Ride', mesS, settings.EMAIL_HOST_USER, [request.user.email])
    send_mass_mail((messageC, messageS), fail_silently=False)

    return redirect(ridesharer)


@login_required
def ridearrvied(request, rideid):
    arrride = Ride.objects.get(id=rideid)
    arrride.status = False
    arrride.save()

    mesC = 'Your ride has completed.'
    mesD = arrride.creator + '\'s ride has completed.'
    messageC = ('Your Ride Has Been Accepted', mesC, settings.EMAIL_HOST_USER, [Userinfo.objects.get(name=arrride.creator).email])
    messageD = ('You Confirm a Ride', mesD, settings.EMAIL_HOST_USER, [Userinfo.objects.get(name=arrride.driver).email])
    send_mass_mail((messageC, messageD), fail_silently=False)

    return redirect(rideowner)


@login_required
def editDriver(request):
    driver = Driver.objects.get(name=request.user.username)

    if request.method=="POST":
        vtype = request.POST["vtype"]
        plateNumber = request.POST["plateNumber"]
        numberOfPassagers = request.POST["numberOfPassagers"]
        specialInfo = request.POST["specialInfo"]
        driver.vtype = vtype
        driver.plateNumber = plateNumber
        driver.numberOfPassagers = numberOfPassagers
        driver.specialInfo = specialInfo
        driver.save()
        return redirect(ridedriver)

    return render(request,"rideshare/editdriverinfo.html", {'driver': driver})