from django.db import models
from authenticate.models import User
from django.contrib.auth import get_user_model
import uuid 
from django.conf import settings
from django.urls import reverse
import os
from validators import validate_file_size
from validators import validate_file_extension

User = get_user_model()

class Doc(models.Model):
    def user_directory_path(instance, filename):
        print(type(instance))
        return 'documents/user_{0}/{1}'.format(str(instance.document_id), filename) 

    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=255, blank=False)
    document=models.FileField(null=False,blank=False,upload_to = user_directory_path, validators=[validate_file_size,validate_file_extension]) 
    author = models.ForeignKey(User, related_name='upload', on_delete=models.CASCADE) 
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.document_id) 



#sharing documents between users 
class Share(models.Model): 
    def user_directory_path(instance, filename):
        print(type(instance))
        return 'documents_shared/user_{0}/{1}'.format(str(instance.document_id), filename) 

    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, related_name='share_docs', on_delete=models.CASCADE) 
    shared_to = models.CharField(max_length=255, blank=False)
    description = models.CharField(max_length=255, blank=False)
    document=models.FileField(null=False,blank=False,upload_to = user_directory_path, validators=[validate_file_size,validate_file_extension]) 
    digital_sign = models.CharField(max_length=10000, blank=False, null = True)
    doc_type = models.CharField(max_length=255, blank=False, null = True)

    def __str__(self):
        return str(self.document_id) 





