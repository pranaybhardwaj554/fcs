from django.contrib import admin
from .models import Transaction, verifyDocuments, claimInsurance
# Register your models here.
admin.site.register(Transaction)
admin.site.register(verifyDocuments)
admin.site.register(claimInsurance)