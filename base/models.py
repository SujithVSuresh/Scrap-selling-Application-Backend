
from pyexpat import model
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager




# Create your models here.
USER_TYPE_CHOICES = (
      ('ScraperAdmin', 'ScraperAdmin'),
      ('ScraperStaff', 'ScraperStaff'),
      ('ScrapSeller', 'ScrapSeller'),
      ('Admin', 'Admin')
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


class Category(models.Model):
    categoryName = models.CharField(max_length=100, null=False, blank=False, verbose_name='Category Name')

    def __str__(self):
        return str(self.categoryName)

TYPE = (
       ("Kg", "Kilogram"),
       ("PCs", "Pieces"),
)        
class Item(models.Model):
    itemName = models.CharField(max_length=100, null=False, blank=False, verbose_name='Item Name')  
    rate = models.IntegerField(null=True, blank=False, verbose_name="Item Rate")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='Item Category')
    unit = models.CharField(max_length = 5, choices=TYPE, null=True, blank=False)

    def __str__(self):
        return str(self.itemName)    



class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    addressName = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    village = models.CharField(max_length=200, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postalCode = models.CharField(max_length=200, null=True, blank=True)
    landmark = models.CharField(max_length=300, null=True, blank=True)
    houseOrFlatNo = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phoneNumber = models.CharField(max_length=12, null=True, blank=True)

    def __str__(self):
        return str(self.user) 
STATUS = (
       ("Requested", "Requested"),
       ("Accepted", "Accepted"),
       ("Completed", "Completed"),
       ("Cancelled", "Cancelled"),
       ("Disabled", "Disabled")
) 

class SellRequest(models.Model):
    items = models.ManyToManyField(Item)
    requestedUser = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='Requested User')
    requestedDate = models.DateField(auto_now_add=True)
    requestStatus = models.CharField(max_length = 10, default="Requested", choices=STATUS, null=True, blank=True)
    pickupAddress = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=False, null=True)
    
    def __str__(self):
        return str(self.requestedUser)  



ORDER_STATUS = (
       ("Accepted", "Accepted"),
       ("Completed", "Completed"),
       ("Request cancelled", "Request cancelled"),
       ("Order cancelled", "Order cancelled"),
       ("Disabled", "Disabled")
) 

class Order(models.Model):
    sellRequest = models.OneToOneField(SellRequest, on_delete=models.CASCADE, null=True, blank=True)
    requestStatus = models.CharField(max_length = 20, default="Accepted", choices=ORDER_STATUS, null=True, blank=True)
    pickupDate = models.DateField()
    acceptedUser = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=False, null=True, related_name='accepted_user', verbose_name='Accepted User')
    totalPrice = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    completedUser = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='completed_user', verbose_name='Completed User')
    completedDate = models.DateTimeField(null=True, blank=True)
    acceptedDate = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.sellRequest)  

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False)       
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=False, blank=False)  
    quantity = models.IntegerField(null=True, blank=False)


class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=False, blank=False)
    reviewedUser = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='Reviewed User')
    reviewText = models.CharField(max_length = 500, null=False, blank=False)
    reviewedDate = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.order)                   

                   
