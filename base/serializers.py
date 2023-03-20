from rest_framework import serializers
from .models import CustomUser, ScraperStaffProfile
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
          

