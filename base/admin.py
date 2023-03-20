from django.contrib import admin
from .models import CustomUser, ScraperAdminProfile, ScraperStaffProfile

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ScraperAdminProfile)
admin.site.register(ScraperStaffProfile)
