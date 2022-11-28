from django.contrib import admin
from .models import Doc
from .models import Share
# Register your models here.
admin.site.register(Doc)

#sharing documents between users 
admin.site.register(Share)
