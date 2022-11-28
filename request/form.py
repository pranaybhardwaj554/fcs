from django import forms
from .models import Requestp
from .models import Requesth

from authenticate.models import Organisations,Users,User

class RequestFormh(forms.ModelForm):
    document_types = [('Prescriptions', 'Prescriptions'), ('Medical Bills', 'Medical Bills'), ('Test Results', 'Test Results'), ('Discharge Summary', 'Discharge Summary'), ('Others', 'Others')]
    doc_type = forms.ChoiceField(choices = document_types) 
    
    class Meta:
        model = Requesth
        fields = ('request_to', 'description', 'doc_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        list = Organisations.objects.all()
        list = list.filter(is_approved=True)
        list = list.filter(user__userType__exact=3)
        self.fields['request_to'].queryset = list

class RequestFormp(forms.ModelForm):
    document_types = [('Prescriptions', 'Prescriptions'), ('Medical Bills', 'Medical Bills'), ('Test Results', 'Test Results'), ('Discharge Summary', 'Discharge Summary'), ('Others', 'Others')]
    doc_type = forms.ChoiceField(choices = document_types) 
    
    class Meta:
        model = Requestp
        fields = ('request_to', 'description', 'doc_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        list =  Users.objects.all()
        list = list.filter(is_approved=True)
        list = list.filter(user__userType__exact=2)
        self.fields['request_to'].queryset = list