from django.db import models
from authenticate.models import User,Users,Organisations
from django.contrib.auth import get_user_model
import uuid
from django.core.validators import MaxValueValidator, MinValueValidator
User = get_user_model()

class Requesth(models.Model):
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_by = models.ForeignKey(User, related_name='request_byh', on_delete=models.CASCADE)
    request_to = models.ForeignKey(Organisations, related_name='request_toh', on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=False)
    doc_type =  models.CharField(max_length=255, blank=False, null = True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

class Requestp(models.Model):
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_by = models.ForeignKey(User, related_name='request_byp', on_delete=models.CASCADE)
    request_to = models.ForeignKey(Users, related_name='request_top', on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=False)
    doc_type =  models.CharField(max_length=255, blank=False, null = True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

class Keys(models.Model): 
    private_key = models.CharField(max_length=10000) 
    public_key = models.CharField(max_length=10000) 
    user = models.ForeignKey(User, related_name='keys', on_delete=models.CASCADE)



