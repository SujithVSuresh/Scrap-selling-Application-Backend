
from django.urls import path
from .views import MyTokenObtainPairView, registerScraper, scraperAdminProfileCreator


urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/scraper/', registerScraper, name='registerScraper'),
    path('scraper/admin/profile-creator/<int:id>/', scraperAdminProfileCreator, name='scraperAdminProfileCreator'),
]