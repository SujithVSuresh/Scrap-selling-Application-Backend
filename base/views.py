
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import ScraperStaffProfileSerializer, UserSerializerWithToken, UserSerializer, ScraperStaffProfile, SellRequestSerializer, OrderSerializer
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .models import Address, CustomUser, ScraperAdminProfile, ScraperStaffProfile, SellRequest, Order
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

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

#scraperStaffAdder
@api_view(['POST'])   
def addStaffToBusiness(request, id):
    data = request.data
    try:
        admin = ScraperAdminProfile.objects.get(user__id=data['id'])
        staff = CustomUser.objects.get(id=id)

        admin.staffs.add(staff)
        staff.is_active = True
        staff.userType = "ScraperStaff"
        staff.save()

        staff_profile = ScraperStaffProfile.objects.create(staff=staff, staffOf=admin.user)

        serializer = UserSerializerWithToken(staff, many=False)


    except Exception as e:

        message = {'detail':e}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)    
    return Response(serializer.data) 


@api_view(['GET'])   
@permission_classes([IsAuthenticated])  
def getAllStaffs(request):
    user = request.user
    try:
        
        #admin = CustomUser.objects.get(id=id)
        staffs = ScraperStaffProfile.objects.filter(staffOf__id=user.id)
        print(staffs)

        serializer = ScraperStaffProfileSerializer(staffs, many=True)
        

    except Exception as e:

        message = {'detail':e}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)    
    return Response(serializer.data) 

@api_view(['PUT', 'DELETE'])   
@permission_classes([IsAuthenticated]) 
def deactivateStaff(request, id):
    user = request.user
    try:
        staff = CustomUser.objects.get(id=id)
        staff.is_active = False
        staff.userType = None
        staff.save()

        admin = ScraperAdminProfile.objects.get(user__id=user.id)
        admin.staffs.remove(staff)

        staff_profile = ScraperStaffProfile.objects.get(staff__id=id)
        print("profile", staff_profile)
        staff_profile.delete()

        serializer = UserSerializer(staff, many=False)
        

    except Exception as e:
        message = {'detail':e}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)    
    return Response(serializer.data)  


@api_view(['GET']) 
@permission_classes([IsAuthenticated]) 
def getAllSellRequests(request):
    try:
        user = request.user
        scraper_admin = ScraperAdminProfile.objects.get(user__id=user.id)
        
        sell_request = SellRequest.objects.filter(requestStatus="Requested", pickupAddress__village=scraper_admin.village)
        print("oops", sell_request)

        serializer = SellRequestSerializer(sell_request, many=True)
    except:
        return Response({"details":"No Sell Request found"})    
    return Response(serializer.data)    

@api_view(['GET']) 
#@permission_classes([IsAuthenticated]) 
def getAllTodaysSellRequests(request):
    try:
        user = request.user
        scraper_admin = ScraperAdminProfile.objects.get(user__id=user.id)

        sell_request = SellRequest.objects.filter(requestStatus="Requested", requestedDate=datetime.today(), pickupAddress__village=scraper_admin.village)
        serializer = SellRequestSerializer(sell_request, many=True)
    except:
        return Response({"details":"No Sell Request found"})    
    return Response(serializer.data) 
        
          
@api_view(['GET']) 
#@permission_classes([IsAuthenticated]) 
def getAllPendingOrders(request):
    try:
        #user = request.user
        #if user.userType=="ScraperAdmin":
        #    accepted_user = user.id
        #if user.userType=="ScraperStaff":
        #    staff = ScraperStaffProfile.objects.get(staff__id=user.id)  
        #    accepted_user = staff.staffOf.id  
        #  acceptedUser__id=accepted_user

        orders = Order.objects.filter(requestStatus="Accepted")
        serializer = OrderSerializer(orders, many=True)
    except:
        return Response({"details":"No Pending orders found"})    
    return Response(serializer.data)  

@api_view(['GET']) 
@permission_classes([IsAuthenticated]) 
def getAllCompletedOrders(request):
    try:
        user = request.user
        if user.userType=="ScraperAdmin":
            accepted_user = user.id
        if user.userType=="ScraperStaff":
            staff = ScraperStaffProfile.objects.get(staff__id=user.id)  
            accepted_user = staff.staffOf.id  

        orders = Order.objects.filter(requestStatus="Completed", acceptedUser__id=accepted_user)
        serializer = OrderSerializer(orders, many=True)
    except:
        return Response({"details":"No Pending orders found"})    
    return Response(serializer.data)    
