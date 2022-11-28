from django.db import models
from django.contrib.auth import get_user_model
from upload.models import Share
from authenticate.models import Organisations
import uuid
User = get_user_model()

class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)
    payment_to = models.CharField(max_length=255, blank=False)
    transaction_done = models.BooleanField(default=False, null = True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%d%H%M%SODR') + str(self.id)
        return super().save(*args, **kwargs)

class verifyDocuments(models.Model):
    document = models.FileField(null=False,blank=False,upload_to = 'documents/')
    share = models.ForeignKey(Share, related_name='share_doc', on_delete=models.CASCADE) 

class claimInsurance(models.Model): 
    request_by = models.ForeignKey(User, related_name='user_by', on_delete=models.CASCADE)
    document = models.FileField(null=False,blank=False,upload_to = 'documents/')
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    share = models.ForeignKey(Share, related_name='share_claim', on_delete=models.CASCADE) 
    claim_approved = models.BooleanField(default = False)
    request_to = models.ForeignKey(Organisations, related_name='claim', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.request_id) 