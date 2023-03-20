
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializerWithToken
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import CustomUser, ScraperAdminProfile

# Create your views here.

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        
        for k, v in serializer.items():
            data[k] = v
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

#Scraper admin and staff registeration.
@api_view(['POST'])    
def registerScraper(request):
    data = request.data
    try:
        user = CustomUser.objects.create(
            first_name=data['name'],
            username=data['username'],
            password=make_password(data['password'])
        )
        user.is_active=False
        user.save()
        serializer = UserSerializerWithToken(user, many=False)
    except:
        message = {'detail':'user with this username already exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)    
    return Response(serializer.data)  

#scraperAdminProfile
@api_view(['POST'])    
def scraperAdminProfileCreator(request, id):
    data = request.data
    try:
        user = CustomUser.objects.get(id=id)
        scraper_admin_profile = ScraperAdminProfile.objects.create(
            user=user,
            businessName=data['businessName'],
            ownerName=data['ownerName'],
            phoneNumber=data['phoneNumber'],
            pincode=data['pincode'],
            village=data['village'],
            subDistrict=data['subDistrict'],
            district=data['district'],
            state=data['state'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )

        user.is_active=True
        user.userType="ScraperAdmin"
        user.save()
        serializer = UserSerializerWithToken(user, many=False)
    except:
        message = {'detail':'profile for this user has already been created'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)    
    return Response(serializer.data)         
