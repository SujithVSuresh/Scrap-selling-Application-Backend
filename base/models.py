
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
