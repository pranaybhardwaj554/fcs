from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from authenticate .models import Organisations,Users,User
from django.core.mail import send_mail
from fcsProject import settings
from django.db.models import Q

# Create your views here.

@login_required(login_url = "/")
def search_org(request):
    if request.user.userType != 1:
        return redirect("/dashboard")
    orgType = {
        3:"Hospitals",
        4:"Pharmacy",
        5:"Insurance Firms"
    }
    qs = Organisations.objects.all()
    qs = qs.filter(is_approved__exact=True)
    qs = qs.filter(Q(user__userType__exact=3) | Q(user__userType__exact=4) | Q(user__userType__exact=5))
    name = request.GET.get('name')
    if name != '' and name is not None:
        qs = qs.filter(Q(name__istartswith=name) | Q(location__icontains=name) | Q(user__email__icontains=name) | Q(org_type__istartswith = name))
    context = {
        'queryset':qs,
        'orgType':orgType
    }
    return render(request, "../templates/searchOrg.html", context)


@login_required(login_url = "/")
def search_professional(request):
    if request.user.userType != 1:
        return redirect("/dashboard")
    qs = Users.objects.all()
    qs = qs.filter(user__userType__exact=2)
    qs = qs.filter(is_approved__exact=True)
    name = request.GET.get('name')
    if name != '' and name is not None:
        qs = qs.filter(Q(firstName__istartswith=name) | Q(address__icontains=name)| Q(user__email__icontains=name) )
    context = {
        'queryset':qs,
    }
    return render(request, "../templates/searchProfessional.html", context)


