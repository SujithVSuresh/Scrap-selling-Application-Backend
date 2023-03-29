from django.contrib import admin
from .models import CustomUser, ScraperAdminProfile, ScraperStaffProfile, SellRequest, Item, Category, Address, Order, Review, OrderItem

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ScraperAdminProfile)
admin.site.register(ScraperStaffProfile)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(SellRequest)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(OrderItem)
