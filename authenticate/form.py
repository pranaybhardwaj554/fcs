from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from .models import User,Users,Organisations
from django.db import transaction

user_type= [
    (1, 'Patient'),
    (2, 'Health Care Professional')
]

org_type= [
    (3, 'Hospitals'),
    (4, 'Pharmacy'),
    (5, 'Insurance Firms')
]

organisation = {3 : 'Hospitals', 4 : 'Pharmacy', 5 : 'Insurance Firms'}
class UsersSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, required=True)
    userType = forms.IntegerField(
        label="Register As?",
        widget=forms.Select(choices=user_type),
        required=True
    )
    firstName = forms.CharField(max_length=100, required=True)
    lastName = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=200, required=True)
    identity_proof = forms.FileField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", 'userType')
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.save()
        users = Users.objects.create(user=user)
        users.firstName = self.cleaned_data.get('firstName')
        users.lastName = self.cleaned_data.get('lastName')
        users.address = self.cleaned_data.get('address')
        users.identity_proof = self.cleaned_data.get('identity_proof')
        users.save()
        print(users)
        return user



class OrganisationsSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, required=True)
    userType = forms.IntegerField(
        label="Register As?",
        widget=forms.Select(choices=org_type),
        required=True
    )
    name = forms.CharField(max_length=100, required=True)
    description = forms.CharField(max_length=200, required = True)
    location = forms.CharField(max_length=200, required = True)
    contactDetails = forms.IntegerField(validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)], required=True)
    image1 = forms.ImageField(required=True)
    image2 = forms.ImageField(required = True)
    license = forms.FileField(required=True)
    permit = forms.FileField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",'userType')
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        # print(user.userType)
        user.save()
        org = Organisations.objects.create(user=user, contactDetails=self.cleaned_data.get('contactDetails'))
        org.org_type = organisation[user.userType]
        org.name = self.cleaned_data.get('name')
        org.description = self.cleaned_data.get('description')
        org.location = self.cleaned_data.get('location')
        org.image1 = self.cleaned_data.get('image1')
        org.image2 = self.cleaned_data.get('image2')
        org.permit = self.cleaned_data.get('permit')
        org.license = self.cleaned_data.get('license')
        org.save()
        return user

class UsersUpdateForm(forms.ModelForm):
    class Meta:
        model = Users
        fields =  ['firstName','lastName','address']

class OrganisationsUpdateForm(forms.ModelForm):
    class Meta:
        model = Organisations
        fields =  ['name','description','location', 'contactDetails', 'image1', 'image2', ]

