
from rest_framework import serializers
from .models import Category, CustomUser, ScraperStaffProfile, Item, SellRequest, Address, Order
from rest_framework_simplejwt.tokens import RefreshToken


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


class SellRequestSerializer(serializers.ModelSerializer):
    items = ItemSerializer(read_only=True, many=True)
    class Meta:
        model = SellRequest
        fields = "__all__" 

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"        

class AddressWithSellRequestSerializer(AddressSerializer):
    sellRequest = SellRequestSerializer(read_only=True)
    class Meta:
        model = Address
        fields = "__all__"  

class OrderSerializer(serializers.ModelSerializer):
    sellRequest = SellRequestSerializer(read_only=True)
    address = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Order
        fields = "__all__"   

    def get_address(self, obj):
        address = Address.objects.get(sellRequest__id=obj.sellRequest.id)
        serializer = AddressSerializer(address)
        return serializer.data                            
          

