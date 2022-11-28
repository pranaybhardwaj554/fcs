from django import forms
from django.db import models
from authenticate.models import User, Users, Organisations
from django.contrib.auth import get_user_model
from .models import verifyDocuments, claimInsurance
from itertools import chain
from django.db.models import Q
from upload.models import Share 
import request 

class verifyForm(forms.ModelForm):

    class Meta:
        model = verifyDocuments 
        fields = ('document','share', )
    
    def __init__(self, *args, **kwargs):
        self._email = kwargs.pop('email', None)
        super().__init__(*args, **kwargs)
        list = Share.objects.all()
        list = list.filter(shared_to__exact = self._email).filter(Q(author__userType__exact=3) | Q(author__userType__exact=2))
        list = list.filter(doc_type__exact = 'Prescriptions')
        self.fields['share'].queryset = list

class claimForm(forms.ModelForm):
    class Meta:
        model = claimInsurance  
        fields = ('document','share', 'request_to')
    
    def __init__(self, *args, **kwargs):
        self._email = kwargs.pop('email', None)
        super().__init__(*args, **kwargs)
        list = Share.objects.all()
        list = list.filter(shared_to__exact = self._email).filter(Q(author__userType__exact=3) | Q(author__userType__exact=2) | Q(author__userType__exact=4) )
        list = list.filter(doc_type__exact = 'Medical Bills')
        self.fields['share'].queryset = list
        list1 = Organisations.objects.all().filter(user__userType__exact = 5)
        self.fields['request_to'].queryset = list1
