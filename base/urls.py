
from django.urls import path
from .views import MyTokenObtainPairView, registerScraper, scraperAdminProfileCreator, addStaffToBusiness, getAllStaffs, deactivateStaff


urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/scraper/', registerScraper, name='registerScraper'),
    path('scraper/admin/profile-creator/<int:id>/', scraperAdminProfileCreator, name='scraperAdminProfileCreator'),
    path('scraper/admin/all-staffs/<int:id>/', getAllStaffs, name='getAllStaffs'),
    path('scraper/admin/deactivate-staff/<int:id>/', deactivateStaff, name='deactivateStaff'),
    path('scraper/staff/add-staff/<int:id>/', addStaffToBusiness, name='addStaffToBusiness'),

]