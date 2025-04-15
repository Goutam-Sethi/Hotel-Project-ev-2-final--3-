from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings



class AppUserManager(BaseUserManager):
    def create_user(self, email, name, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is mandatory')  
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Superusers must have a password.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, name, phone, password, **extra_fields)

class AppUser(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    username = None
    objects = AppUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    def __str__(self):
        return self.email

class Property(models.Model):
    hotel_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    license_number = models.CharField(max_length=100)
    rooms_available = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    owner = models.ForeignKey(AppUser, on_delete=models.CASCADE,default="1")

    def __str__(self):
        return self.hotel_name

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    user_name = models.CharField(max_length=100)
    user_phone = models.CharField(max_length=15)
    user_email = models.EmailField()
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    rooms_booked = models.IntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.property.hotel_name} ({self.booked_at.strftime('%Y-%m-%d %H:%M')})"
    
