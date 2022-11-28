from django.shortcuts import render, redirect
from django.views.generic import CreateView
from .models import User, Users, Organisations
from .form import UsersSignUpForm, OrganisationsSignUpForm, UsersUpdateForm, OrganisationsUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.mail import send_mail
import base64
import pyotp
import string, random
from datetime import datetime
from fcsProject import settings
from request.models import Keys 
from Crypto.PublicKey import RSA
from ratelimit import limits, RateLimitException
from requests_ratelimiter import LimiterSession
from backoff import on_exception, expo


# 30 calls per minute
CALLS = 2
RATE_LIMIT = 50

@on_exception(expo, RateLimitException, max_tries=2)
@limits(calls=CALLS, period=RATE_LIMIT)
def check_limit():
    ''' Empty function just to check for calls to API '''
    return

def register(request):
    if(str(request.user) != "AnonymousUser"):
        return redirect("/dashboard")
    return render(request, "../templates/register.html")

def index(request):
    return render(request, "../templates/index.html")


def login_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = AuthenticationForm(data = request.POST)
            if form.is_valid():
                email = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(email=email, password=password)
                if user is not None:
                    usr = Users.objects.get(user = user) if user.userType < 3 else Organisations.objects.get(user = user)
                    if usr.is_approved:
                        #rate limit
                        # try:
                        #     check_limit()
                        # except:
                        #     return redirect('/')
                        # else:
                        #     print("Nothing went wrong")
                        try: 
                            check_limit()
                            request.session['otp_user_id'] = email
                            keygen = generate_key(''.join(random.choices(string.ascii_uppercase + string.digits, k=10))) + email
                            key = base64.b32encode(keygen.encode())
                            OTP = pyotp.TOTP(key, interval=120)
                            subject = 'OTP validation'
                            message = 'Hey,\nBelow is the 6 digit otp:\n' + str(
                                OTP.now()) + '\n\nthis is a system generated mail. Do not reply'
                            email_from = settings.EMAIL_HOST_USER
                            recipient_list = [email]
                            send_mail(subject, message, email_from, recipient_list)
                            request.session['otp_key'] = keygen
                            return redirect("/otp")
                        except: 
                            messages.error(request, "Too many requests : Wait for a minute before logging in")
                            return redirect('/login')

                    else:
                        messages.error(request, "You are not approved by admin yet")
                        return redirect('/')
                else:
                    messages.error(request, "Invalid Username or password")
                    return redirect('/login')

            else:
                messages.error(request, "Invalid Username or password")
                return redirect('/login')
        return render(request, "../templates/login.html", context = {'form':AuthenticationForm})

    else:
        return redirect('/dashboard')


def register_org(request):
    if (str(request.user) != "AnonymousUser"):
        return redirect("/dashboard")
    form = OrganisationsSignUpForm()
    if request.method == 'POST':
        form = OrganisationsSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/")
        else:
            return render(request, '../templates/register_org.html', {'form': form})
    return render(request, "../templates/register_org.html",{'form':form})


def register_user(request):
    if (str(request.user) != "AnonymousUser"):
        return redirect("/dashboard")
    form = UsersSignUpForm()
    if request.method == 'POST':
        form = UsersSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/")
        else:
            return render(request, '../templates/register_user.html', {'form': form})
    return render(request, "../templates/register_user.html",{'form':form})


@login_required(login_url="/")
def logout_view(request):
    logout(request)
    return redirect('/')

@login_required(login_url = "/")
def dashboard(request):
    if request.user.userType == 1:
        return render(request, "../templates/dashboardPatient.html")
    elif request.user.userType == 2:
        return render(request, "../templates/dashboardProfessional.html")
    elif request.user.userType == 3:
        return render(request, "../templates/dashboardHospital.html")
    elif request.user.userType == 4:
        return render(request, "../templates/dashboardPharmacy.html")
    elif request.user.userType == 5:
        return render(request, "../templates/dashboardInsurance.html")
    return render(request, "../templates/dashboardOrg.html")

@login_required(login_url = "/")
def profile(request):
    if request.method == 'POST':
        form = UsersUpdateForm(request.POST, instance=request.user.users) if ((request.user.userType == 1) or (request.user.userType == 2)) else OrganisationsUpdateForm(request.POST, request.FILES, instance=request.user.organisations)

        if form.is_valid():
            form.save()
            messages.success(request, f'Your Profile has been updated')
            return redirect('profile')
    else:
        form = UsersUpdateForm(instance=request.user.users) if ((request.user.userType == 1) or (request.user.userType == 2)) else OrganisationsUpdateForm(instance=request.user.organisations)

    context = {
        'form': form
    }
    return render(request, "../templates/profile.html", context)



# @limits(calls=1, period=30)
def otp(request):
    # check_limit()
    # response1 = session.get('http://127.0.0.1:8000/login')
    # response2 = session.get('http://127.0.0.1:8000/otp/')
    # print('hi')
    # print(response1.json)
    # print(response2.json)
    if request.user.is_authenticated:
        return redirect('/dashboard')

    if 'otp_user_id' not in request.session.keys():
        return redirect('/login')

    if request.method == "POST":
        # check_limit()
        keygen = request.session["otp_key"]
        key = base64.b32encode(keygen.encode())
        print("Otpis",keygen)
        request.session.pop('otp_key')
        OTP = pyotp.TOTP(key, interval=120) #Expiry time is 2 mintues
        user = User.objects.get(email = request.session['otp_user_id'])
        request.session.pop('otp_user_id')
        print(request.POST['otp'])
        if OTP.verify(request.POST['otp']):
            login(request, user)
            request.session['otpPayment'] = False
            request.session['docVerified'] = False
            key = Keys.objects.all().filter(user__exact = request.user)
            if(len(key) == 0 ): 
                private_key = RSA.generate(2048)
                pubkey = private_key.publickey()
                private_key = private_key.exportKey().decode("utf-8")
                pubkey = pubkey.exportKey().decode("utf-8")
                key1 = Keys.objects.create(user = request.user , private_key = private_key, public_key = pubkey)
                key1.save()
            return redirect("/dashboard")
        else:
            return HttpResponse(f"<h1>Error</h1><p> Otp was wrong or expired </p><p><a href='/login'>Try again</a></p>")

    user = User.objects.get(email = request.session['otp_user_id'])
    args = {"email":user.email}

    return render(request, "../templates/otp.html", args)

def generate_key(random_string):
    return str(datetime.date(datetime.now())) + random_string
