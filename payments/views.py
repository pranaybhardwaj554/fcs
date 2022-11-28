import hashlib

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from django.contrib import messages
from django.views.generic import (
    ListView,
)
from authenticate.views import generate_key
from request.models import Keys
from .models import Transaction, claimInsurance
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template import loader
from authenticate.models import User, Users, Organisations
from django.contrib.auth.decorators import login_required
import random,string,base64,pyotp
from .form import verifyForm, claimForm
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
DATA = {}
DATA_2 = {}
@login_required(login_url = "/")
def initiate_payment_patient(request):
    if request.user.userType != 1:
        return redirect("/dashboard")
    org = Organisations.objects.filter(is_approved__exact = True).values_list("user",  "name")
    mymembers = []
    for id1, name in org: 
        qs = User.objects.filter(id__exact = id1, userType__exact = 4).values("email")
        if(len(qs) > 0): 
            email = qs[0]['email']
            mymembers.append(email)
        
    if request.method == "GET" and request.session['otpPayment'] and request.session["docVerified"]:
        request.session['otpPayment'] = False
        request.session["docVerified"] = False
        print('fewrg')
        return render(request, 'payments/pay_patient.html',  {'mymembers': mymembers})
    elif request.method == "GET" and not request.session['otpPayment']:
        keygen = generate_key(''.join(random.choices(string.ascii_uppercase + string.digits, k=10))) + request.user.email
        key = base64.b32encode(keygen.encode())
        OTP = pyotp.TOTP(key, interval=120)
        subject = 'OTP validation'
        message = 'Hey,\nBelow is the 6 digit otp:\n' + str(
            OTP.now()) + '\n\nthis is a system generated mail. Do not reply'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email]
        send_mail(subject, message, email_from, recipient_list)
        request.session['otp_key'] = keygen
        request.session['otp_type'] = 'patient'
        return redirect("/otppayment")
    try:
        username = request.POST['username']
        password = request.POST['password']
        amount = int(request.POST['amount'])
        user = authenticate(request, username=username, password=password)
        if user is None:
            print('?')
            raise ValueError
        if (user.email != request.user.email): 
            # print('frf')
            # print(user)
            # print(request.user)
            # print(user.email)
            # print(request.user.email)
            raise ValueError
        auth_login(request=request, user=user)
    except:
        return render(request, 'payments/pay_patient.html', context={'error': 'Wrong Account Details or amount', 'mymembers': mymembers})

    transaction = Transaction.objects.create(made_by=user, amount=amount, payment_to = request.POST['payment_to'])
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('PAYED_TO', str(transaction.payment_to)), 
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)
    # request.session['t_id'] = transaction.order_id

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    paytm_params['PAYED_TO'] = transaction.payment_to
    global DATA 
    DATA = paytm_params
    print(checksum)
    return render(request, 'payments/redirect.html', context=paytm_params)

@login_required(login_url="/")
def otppayment(request):
    if request.user.userType not in [1, 5]:
        return redirect("/dashboard")

    if "otp_key"not in request.session:
        return redirect("/dashboard")

    if request.session['otp_type'] == 'patient' and not request.session['docVerified']:
        return redirect("/verifyDocs")
    if request.method == "POST":
        keygen = request.session["otp_key"]
        key = base64.b32encode(keygen.encode())
        print("Otpis",keygen)
        request.session.pop('otp_key')
        OTP = pyotp.TOTP(key, interval=120) #Expiry time is 2 mintues
        user = request.user
        print(request.POST['otp'])
        if OTP.verify(request.POST['otp']):
            request.session['otpPayment'] = True
            if request.session['otp_type'] == 'patient':
                return redirect("/pay_patient")
            else:
                return redirect("/pay_insurance")
        else:
            return HttpResponse(f"<h1>Error</h1><p> Otp was wrong or expired </p><p><a href='/login'>Try again</a></p>")

    user = request.user
    args = {"email":user.email}
    return render(request, "../templates/otp.html", args)


@login_required(login_url = "/")
def initiate_payment_insurance(request):
    if request.user.userType != 5:
        return redirect("/dashboard")

    if('claimSelect' not in request.session.keys()): 
        return redirect('/dashboard')
    
    # org = Users.objects.filter(is_approved__exact = True).values_list("user",  "firstName")
    # mymembers = []
    # for id1, name in org: 
    #     qs = User.objects.filter(id__exact = id1, userType__exact = 1).values("email")
    #     if(len(qs) > 0): 
    #         email = qs[0]['email']
    #         mymembers.append(email)
    uuid = request.session
    mymember = []
    mymember.append(request.session['email'])
    print(mymember, "email is this")
    if request.method == "GET" and request.session['otpPayment']:
        request.session['otpPayment'] = False
        return render(request, 'payments/pay_insurance.html', {'mymembers': mymember})
    elif request.method == "GET" and not request.session['otpPayment']:
        keygen = generate_key(
            ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))) + request.user.email
        key = base64.b32encode(keygen.encode())
        OTP = pyotp.TOTP(key, interval=120)
        subject = 'OTP validation'
        message = 'Hey,\nBelow is the 6 digit otp:\n' + str(
            OTP.now()) + '\n\nthis is a system generated mail. Do not reply'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email]
        send_mail(subject, message, email_from, recipient_list)
        request.session['otp_key'] = keygen
        request.session['otp_type'] = 'insurance'
        return redirect("/otppayment")


    try:
        username = request.POST['username']
        password = request.POST['password']
        amount = int(request.POST['amount'])
        user = authenticate(request, username=username, password=password)
        if user is None:
            raise ValueError
        if (user.email != request.user.email): 
            raise ValueError
        auth_login(request=request, user=user)
    except:
        return render(request, 'payments/pay_insurance.html', context={'error': 'Wrong Accound Details or amount', 'mymembers': mymember})

    transaction = Transaction.objects.create(made_by=user, amount=amount, payment_to = request.POST['payment_to'])
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(request.user)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('PAYED_TO', str(transaction.payment_to)), 
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    
    checksum = generate_checksum(paytm_params, merchant_key)
    paytm_params['user'] = user
    transaction.checksum = checksum
    # request.session['t_id'] = transaction.order_id
    # request.session['transaction'] = transaction
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum

    print('SENT: ', checksum)
    paytm_params['PAYED_TO'] = transaction.payment_to
    global DATA 
    DATA = paytm_params
    return render(request, 'payments/redirect.html', context = paytm_params) 


@login_required(login_url = "/")
def verifyDoc(request): 
    form = verifyForm(email = request.user.email)
    if(request.method == 'POST'): 
        form = verifyForm(request.POST, request.FILES, email = request.user.email) 
        if(form.is_valid()): 
            # Document verification
            file = request.FILES['document']
            doc = form.cleaned_data['share']
            string = file.read()
            m = SHA256.new(string)
            me = Keys.objects.all().filter(user__exact=doc.author)
            public_key = me[0].public_key
            public_key = RSA.import_key(public_key)
            signature = doc.digital_sign.split(" ")
            n = []
            for i in signature:
                n.append(int(i))
            signature = bytes(n)
            a = True
            try:
                pkcs1_15.new(public_key).verify(m, signature)
            except:
                a = False
            if a:
                request.session['docVerified'] = True
                return redirect("/otppayment")
            else:
                messages.error(request, "Digital Signature and Uploaded Document doesn't matches")
                return redirect('/verifyDocs')

    else:
            return render(request, '../templates/verifyDocs.html',  {'form' : form} )
    
    return render(request, '../templates/verifyDocs.html', {'form' : form} )

class Sales(ListView):
    model = Transaction
    template_name = '../templates/sales.html'
    context_object_name = 'sale'
   
    def get_queryset(self):
        if self.request.user.userType != 4:
            return redirect("/dashboard")
        return Transaction.objects.filter(payment_to__exact=self.request.user.email)

@login_required(login_url = "/")
def reqClaim(request):
    if request.user.userType != 1:
        return redirect("/dashboard")
    form = claimForm(email = request.user.email)
    if(request.method == 'POST'): 
        form = claimForm(request.POST, request.FILES, email = request.user.email) 
        if(form.is_valid()): 
            # Document verification
            file = request.FILES['document']
            doc = form.cleaned_data['share']
            string = file.read()
            m = SHA256.new(string)
            me = Keys.objects.all().filter(user__exact=doc.author)
            public_key = me[0].public_key
            public_key = RSA.import_key(public_key)
            signature = doc.digital_sign.split(" ")
            n = []
            for i in signature:
                n.append(int(i))
            signature = bytes(n)
            a = True
            try:
                pkcs1_15.new(public_key).verify(m, signature)
            except:
                a = False
            if a:
                claimI = claimInsurance.objects.create(request_by = request.user, request_to = form.cleaned_data['request_to'], share = form.cleaned_data['share'], document =  form.cleaned_data['document'])
                claimI.save()
                return redirect("/dashboard")
            else:
                messages.error(request, "Digital Signature and Uploaded Document doesn't match")
                return redirect('/claim')

        else:
            return render(request, '../templates/claim.html',  {'form' : form} )
    
    return render(request, '../templates/claim.html', {'form' : form} )

@login_required(login_url = "/")
def list_claims(request):
    if request.user.userType != 5:
        return redirect("/dashboard")
    qr = claimInsurance.objects.all().filter(request_to__user__email__exact = request.user.email)
    qr = qr.filter(claim_approved__exact = False)
    if (request.method == "POST"): 
        uuid = request.POST['id']
        us = claimInsurance.objects.all().filter(request_id__exact = uuid)
        request.session['claimSelect'] = True
        request.session['email'] = us[0].request_by.email
        global DATA_2
        DATA_2['request_id'] = str(us[0].request_id) 
        # request.session['request_id'] = str(us[0].request_id) 
        return redirect('/pay_insurance')

    return render(request, "../templates/list_claims.html", {'queryset' : qr})

@csrf_exempt
# @login_required(login_url = "/")
def callback(request):
    print('call1', "t_id" in request.session.keys(),"email" in request.session.keys(),request.session.keys() )
    if request.method == 'POST':
        print('post')
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'payments/callback.html', context=received_data)
        # received_data['PAYMENT_TO'] = request.POST['payment_to']
        print(paytm_params)
        received_data['CUST_ID'] = DATA['CUST_ID']
        received_data['PAYED_TO'] = DATA['PAYED_TO']
        print(received_data)
        if(received_data['STATUS'][0] == 'TXN_SUCCESS'): 
            id = DATA['ORDER_ID']
            my_tranact = Transaction.objects.all().filter(order_id__exact = id).update(transaction_done = True)
            # request.session.pop('t_id')
            if 'request_id' in DATA_2.keys(): 
                claimInsurance.objects.all().filter(request_id__exact = DATA_2['request_id']).update(claim_approved = True)
                DATA_2.pop('request_id', None)
                # request.session.pop("claimSelect")
                # request.session.pop("email")
                # # request.session.pop("request_id")
        return render(request, 'payments/callback.html', context=received_data)

