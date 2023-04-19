
from unicodedata import category
from rest_framework import serializers
from .models import Category, CustomUser, ScraperStaffProfile, Item, SellRequest, Address, Order, ScraperAdminProfile, Review,  OrderItem
from rest_framework_simplejwt.tokens import RefreshToken
from geopy.distance import distance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', "first_name", 'is_active', 'userType', "date_joined"]


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

class ScraperAdminProfileSerializer(UserSerializer):
    user = UserSerializer()
    
    class Meta:
        model = ScraperAdminProfile
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

class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = "__all__"                

class CategorySerializerWithItems(CategorySerializer):
    items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = "__all__" 

    def get_items(self, obj):
        item_list = Item.objects.filter(category__id=obj.id) 
        serializer = ItemSerializer(item_list, many=True)
        return serializer.data     

       


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"  

class SellRequestSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField(read_only=True)
    requestedUser = UserSerializer(read_only=True)
    pickupAddress = AddressSerializer(read_only=True)

    class Meta:
        model = SellRequest
        fields = ["id", "data", "requestedDate", "requestStatus", "requestedUser", "pickupAddress"] 

    def get_data(self, obj):
        items = obj.items.all()
        serializer = ItemSerializer(items, many=True)
        return serializer.data    

    


class SellRequestWithDistanceSerializer(SellRequestSerializer):
    data = serializers.SerializerMethodField(read_only=True)
    requestedUser = UserSerializer(read_only=True)
    pickupAddress = AddressSerializer(read_only=True)
    distance = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = SellRequest
        fields = ["id", "data", "pickupAddress", "requestedDate", "requestStatus", "requestedUser", "distance"] 

    def get_data(self, obj):
        items = obj.items.all()
        serializer = ItemSerializer(items, many=True)
        return serializer.data

    def get_distance(self, obj):
        user_id = self.context.get("user_id")
        requested_user = obj.pickupAddress
        #requested user coordinates
        requested_user_latitude = requested_user.latitude
        requested_user_longitude = requested_user.longitude
        accepted_user = ScraperAdminProfile.objects.get(user__id=user_id)
        #accepted user coordinates
        accepted_user_latitude = accepted_user.latitude 
        accepted_user_longitude = accepted_user.longitude 

        dist = distance((accepted_user_latitude, accepted_user_longitude), (requested_user_latitude, requested_user_longitude)).km
        return dist       

class OrderSerializer(serializers.ModelSerializer):
    sellRequest = SellRequestSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = "__all__"   



class OrderSerializerWithDistance(OrderSerializer):
    distance = serializers.SerializerMethodField(read_only=True)
    orderItems = serializers.SerializerMethodField(read_only=True)
    acceptedUser = UserSerializer(read_only=True)
    completedUser = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = "__all__"   

    def get_distance(self, obj):

        requested_user = obj.sellRequest.pickupAddress
        #requested user coordinates
        requested_user_latitude = requested_user.latitude
        requested_user_longitude = requested_user.longitude
        print("obj", obj)
        accepted_user = ScraperAdminProfile.objects.get(user__id=obj.acceptedUser.id)
        
        #accepted user coordinates
        accepted_user_latitude = accepted_user.latitude 
        accepted_user_longitude = accepted_user.longitude 

        dist = distance((accepted_user_latitude, accepted_user_longitude), (requested_user_latitude, requested_user_longitude)).km
        return dist 

    def get_orderItems(self, obj):
        #sellrequest_order = Order.objects.get(sellRequest__id=obj.id)
        try:
            order_items = OrderItem.objects.filter(order__id=obj.id)
            serializer = OrderItemSerializer(order_items, many=True)
            return serializer.data
        except OrderItem.DoesNotExist:  
            return None    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"       

class OrderSerializerForSellRequest(OrderSerializer):
    acceptedUser = serializers.SerializerMethodField(read_only=True)
    completedUser = UserSerializer(read_only=True)
    review = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "requestStatus", "pickupDate","acceptedUser", "totalPrice", "completedUser", "completedDate", "acceptedDate", "review"] 
    
    def get_acceptedUser(self, obj):
        #sellrequest_order = Order.objects.get(sellRequest__id=obj.id)
        try:
            accepted_user = ScraperAdminProfile.objects.get(user__id=obj.acceptedUser.id)
            serializer = ScraperAdminProfileSerializer(accepted_user, many=False)
            return serializer.data
        except Order.DoesNotExist:  
            return None

    def get_review(self, obj):
        try:
            review = Review.objects.get(order__id=obj.id)
            serializer = ReviewSerializer(review, many=False)
            return serializer.data
        except Review.DoesNotExist:  
            return None

class SellRequestSerializerWithOrder(SellRequestSerializer):
    order = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SellRequest
        fields = ["id", "data", "pickupAddress", "requestedDate", "requestStatus", "requestedUser", "order"] 

    def get_order(self, obj):
        #sellrequest_order = Order.objects.get(sellRequest__id=obj.id)
        try:
            sellrequest_order = Order.objects.get(sellRequest__id=obj.id)
            serializer = OrderSerializerForSellRequest(sellrequest_order, many=False)
            return serializer.data
        except Order.DoesNotExist:  
            return None



class UserSerializerForScraperAdmin(UserSerializer):
    profileInfo = serializers.SerializerMethodField(read_only=True)
    staffs = serializers.SerializerMethodField(read_only=True)
    acceptedOrders = serializers.SerializerMethodField(read_only=True)
    completedOrders = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "date_joined", "is_active", "profileInfo", "staffs", "acceptedOrders", "completedOrders"] 


    def get_profileInfo(self, obj):
        try:
            profile = ScraperAdminProfile.objects.get(user__id=obj.id)
            serializer = ScraperAdminProfileSerializer(profile, many=False)
            return serializer.data
        except ScraperAdminProfile.DoesNotExist:  
            return None   

    def get_staffs(self, obj):
        try:
            profile = ScraperAdminProfile.objects.get(user__id=obj.id)
            staffs = profile.staffs.all().count()
            return staffs
        except ScraperAdminProfile.DoesNotExist:  
            return None

    def get_acceptedOrders(self, obj):
        try:
            orders = Order.objects.filter(requestStatus__in=["Accepted"], acceptedUser__id=obj.id)
            order_count = orders.count()
            return order_count
        except ScraperAdminProfile.DoesNotExist:  
            return None

    def get_completedOrders(self, obj):
        try:
            orders = Order.objects.filter(requestStatus__in=["Completed"], acceptedUser__id=obj.id)
            order_count = orders.count()
            return order_count
        except ScraperAdminProfile.DoesNotExist:  
            return None 


class UserSerializerForScraperStaff(UserSerializer):
    staffProfile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "date_joined", "is_active", "staffProfile"] 


    def get_staffProfile(self, obj):
        try:
            profile = ScraperStaffProfile.objects.get(staff__id=obj.id)
            serializer =  ScraperStaffProfileSerializer(profile, many=False)
            return serializer.data
        except ScraperStaffProfile.DoesNotExist:  
            return None  


class UserSerializerForScrapSeller(UserSerializer):
    sellRequests = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "date_joined", "is_active", "sellRequests"] 


    def get_sellRequests(self, obj):
        try:
            sell_requests = SellRequest.objects.filter(requestedUser__id=obj.id)
            sell_requests_count = sell_requests.count()
            return sell_requests_count
        except SellRequest.DoesNotExist:  
            return None               
                                                            
                      

      

           


                          
          

