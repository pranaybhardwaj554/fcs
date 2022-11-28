from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .form import RequestFormp, RequestFormh
from .models import Requesth,Requestp

@login_required(login_url = "/")
def requestp(request):
    if request.user.userType != 1:
        return redirect("/dashboard")
    form = RequestFormp()
    if request.method == 'POST':
        form = RequestFormp(request.POST)
        if form.is_valid():
            req = Requestp.objects.create(request_by=request.user, request_to=form.cleaned_data['request_to'], description=form.cleaned_data["description"], doc_type = form.cleaned_data["doc_type"])
            req.save()
            return redirect("/dashboard/")
        else:
            return render(request, '../templates/request.html', {'form': form})
    return render(request, "../templates/request.html", {'form':form})

@login_required(login_url = "/")
def requesth(request):
    if request.user.userType != 1:
        return redirect("/dashboard")
    form = RequestFormh()
    if request.method == 'POST':
        form = RequestFormh(request.POST)
        if form.is_valid():
            req = Requesth.objects.create(request_by=request.user, request_to=form.cleaned_data['request_to'], description=form.cleaned_data["description"], doc_type = form.cleaned_data["doc_type"])
            req.save()
            return redirect("/dashboard/")
        else:
            return render(request, '../templates/request.html', {'form': form})
    return render(request, "../templates/request.html", {'form':form})

@login_required(login_url="/")
def requests(request):
    if request.user.userType == 2:
        qr = Requestp.objects.all()
    else:
        qr = Requesth.objects.all()
    qr = qr.filter(request_to__user__email__exact=request.user.email)
    qr = qr.filter(is_approved__exact=False)
    if request.method == "POST":
        uuid = request.POST['id']
        if request.user.userType == 2: 
            qr = Requestp.objects.all().filter(request_id__exact=uuid).update(is_approved=True)
        else: 
            qr = Requesth.objects.all().filter(request_id__exact=uuid).update(is_approved=True)
        return redirect("/dashboard")
    return render(request, "../templates/displayrequests.html",{'queryset':qr})

