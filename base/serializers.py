
from rest_framework import serializers
from .models import Category, CustomUser, ScraperStaffProfile, Item, SellRequest, Address, Order, ScraperAdminProfile
from rest_framework_simplejwt.tokens import RefreshToken
from geopy.distance import distance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', "first_name", 'is_active', 'userType']


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', "first_name", 'is_active', 'userType', 'token']    

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        token = str(token.access_token) 
        return token   

class ScraperStaffProfileSerializer(UserSerializer):
    staff = UserSerializer(read_only=True)
    staffOf = UserSerializer(read_only=True)
    class Meta:
        model = ScraperStaffProfile
        fields = "__all__"   

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"     

class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Item
        fields = "__all__"   


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"         

class SellRequestSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField(read_only=True)
    pickupAddress = AddressSerializer(read_only=True)
    class Meta:
        model = SellRequest
        fields = ["id", "data", "pickupAddress", "requestedDate", "requestStatus", "requestedUser"] 

    def get_data(self, obj):
        items = obj.items.all()
        serializer = ItemSerializer(items, many=True)
        return serializer.data   

class OrderSerializer(serializers.ModelSerializer):
    sellRequest = SellRequestSerializer(read_only=True)
    acceptedUser = UserSerializer(read_only=True)
    distance = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Order
        fields = "__all__"   

    def get_distance(self, obj):
        requested_user = obj.sellRequest.pickupAddress
        #requested user coordinates
        requested_user_latitude = requested_user.latitude
        requested_user_longitude = requested_user.longitude
        accepted_user = ScraperAdminProfile.objects.get(user__id=obj.acceptedUser.id)
        #accepted user coordinates
        accepted_user_latitude = accepted_user.latitude 
        accepted_user_longitude = accepted_user.longitude 

        dist = distance((accepted_user_latitude, accepted_user_longitude), (requested_user_latitude, requested_user_longitude)).km
        return dist


                          
          

