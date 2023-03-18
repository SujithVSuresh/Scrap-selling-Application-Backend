from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'is_active', 'userType']


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'is_active', 'userType', 'token']    

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        token = str(token.access_token) 
        return token   

