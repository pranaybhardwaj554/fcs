from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
import uuid 
from validators import validate_file_size
from validators import validate_file_extension

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.UUIDField(default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    userType = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Users(models.Model):
    def user_directory_path(instance, filename):
        print(type(instance))
        return 'identity/user_{0}/{1}'.format(str(instance.user.username), filename) 

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    is_approved = models.BooleanField(default=False)
    identity_proof = models.FileField(null=False,blank=False,upload_to = user_directory_path, validators=[validate_file_size,validate_file_extension])

    def __str__(self):
        return self.user.email

class Organisations(models.Model):
    def user_directory_path(instance, filename):
        print(type(instance))
        return 'license/user_{0}/{1}'.format(str(instance.user.username), filename) 

    def user_directory_path1(instance, filename):
        print(type(instance))
        return 'permits/user_{0}/{1}'.format(str(instance.user.username), filename) 

    def user_directory_path2(instance, filename):
        print(type(instance))
        return 'images/user_{0}/{1}'.format(str(instance.user.username), filename) 

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    contactDetails = models.IntegerField(validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)])
    image1 = models.ImageField(upload_to=user_directory_path2, validators=[validate_file_size])
    image2 = models.ImageField(upload_to=user_directory_path2, validators=[validate_file_size])
    is_approved = models.BooleanField(default=False)
    license = models.FileField(null = False, blank=False,upload_to = user_directory_path, validators=[validate_file_size,validate_file_extension])
    permit = models.FileField(null=False,blank=False,upload_to = user_directory_path1, validators=[validate_file_size,validate_file_extension])
    org_type = models.CharField(max_length=200, null = True)

    def __str__(self):
        return self.user.email






