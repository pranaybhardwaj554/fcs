from django.core.exceptions import ValidationError
import os
def validate_file_size(value):
    filesize= value.size
    
    if filesize > 10485760:
        raise ValidationError("You cannot upload file more than 10Mb")
    else:
        return value

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension. Valid extensions - '.pdf', '.doc', '.docx', '.jpg', '.png'")