
from pyexpat import model
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager




# Create your models here.
USER_TYPE_CHOICES = (
      ('ScraperAdmin', 'ScraperAdmin'),
      ('ScraperStaff', 'ScraperStaff'),
      ('ScrapSeller', 'ScrapSeller')
    )
class CustomUser(AbstractUser):
    email = None
    username = models.CharField(max_length=15, unique=True)
    userType = models.CharField(choices=USER_TYPE_CHOICES, null=True, max_length=100)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.username

class ScraperAdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name="scraperadmin")
    businessName = models.CharField(max_length=100, null=False, blank=False, verbose_name='Business Name')
    ownerName = models.CharField(max_length=100, null=False, blank=False, verbose_name='Owner Name')
    phoneNumber = models.CharField(max_length=100, null=False, blank=False, verbose_name='PhoneNumber')
    pincode = models.CharField(max_length=100, null=False, blank=False, verbose_name='Pincode')
    village = models.CharField(max_length=100, null=False, blank=False, verbose_name='Village Name')
    subDistrict = models.CharField(max_length=100, null=False, blank=False, verbose_name='SubDistrict')
    district = models.CharField(max_length=100, null=False, blank=False, verbose_name='District')
    state = models.CharField(max_length=100, null=False, blank=False, verbose_name='State Name')
    staffs = models.ManyToManyField(CustomUser, related_name="scraperstaffs", blank=True)
    latitude = models.DecimalField(max_digits=9, null=True, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, null=True, decimal_places=6)

    def __str__(self):
        return str(self.businessName)



class ScraperStaffProfile(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='Staff', related_name="staff")
    staffOf = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='Admin', related_name="admin")
    dateJoined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.staff)        
