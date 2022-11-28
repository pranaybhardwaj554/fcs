from django.urls import path
from .views import initiate_payment_patient, callback, initiate_payment_insurance,otppayment, verifyDoc, reqClaim, list_claims
from .views import (
    Sales
)
urlpatterns = [
    path('pay_patient/', initiate_payment_patient, name='pay_patient'),
    path('callback/', callback, name='callback'),
    path('pay_insurance/', initiate_payment_insurance, name='pay_insurance'),
    path('list_claims/', list_claims, name='list_claims'),
    path('otppayment/', otppayment, name='otp-payment'),
    path('verifyDocs/', verifyDoc, name='verifyDocs'),
    path('sales/', Sales.as_view(), name='sales'),
    path('claim/',reqClaim, name='claim'),
]