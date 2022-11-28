from django import forms
from django.db import models
from authenticate.models import User, Users, Organisations
from django.contrib.auth import get_user_model
from .models import Doc, Share 
from itertools import chain
from django.db.models import Q


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Doc
        fields = ('description', 'document')

class ShareForm(forms.ModelForm): 
    qs1 = Users.objects.filter(is_approved__exact = True).values_list("user", "firstName")
    qs2 = Organisations.objects.filter(is_approved__exact = True).values_list("user",  "name")
    lis =  list(chain(qs1, qs2))
    choice = []
    for id1, name in lis: 
        email = User.objects.filter(id__exact = id1).values("email") [0]['email']
        choice.append((email, email))
    shared_to = forms.ChoiceField(choices = choice) 
    document_types = [('Prescriptions', 'Prescriptions'), ('Medical Bills', 'Medical Bills'), ('Test Results', 'Test Results'), ('Discharge Summary', 'Discharge Summary'), ('Others', 'Others')]
    doc_type = forms.ChoiceField(choices = document_types) 
    


    class Meta: 
        model = Share
        fields = ('description', 'document', 'shared_to', 'doc_type')
        


        