
from operator import truediv
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import AddressSerializer, UserSerializerForScraperAdmin,  UserSerializerForScrapSeller, UserSerializerForScraperStaff, CategorySerializer, ItemSerializer, SellRequestSerializerWithOrder, OrderSerializerWithDistance, ReviewSerializer, ScraperStaffProfileSerializer, UserSerializerWithToken, UserSerializer, ScraperStaffProfile, SellRequestSerializer, OrderSerializer, SellRequestWithDistanceSerializer, CategorySerializerWithItems

from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .models import Address, Category, CustomUser, Item, ScraperAdminProfile, ScraperStaffProfile, SellRequest, Order, OrderItem, Review
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date, timedelta




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

        serializer = SellRequestWithDistanceSerializer(sell_request, many=True, context={'user_id': user.id})
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
        serializer = SellRequestWithDistanceSerializer(sell_request, many=True, context={'user_id': user.id})
    except:
        return Response({"details":"No Sell Request found"})    
    return Response(serializer.data) 
        
          
@api_view(['GET']) 
@permission_classes([IsAuthenticated]) 
def getAllPendingOrders(request):
    try:
        user = request.user
        if user.userType=="ScraperAdmin":
            accepted_user = user.id
        if user.userType=="ScraperStaff":
            staff = ScraperStaffProfile.objects.get(staff__id=user.id)  
            accepted_user = staff.staffOf.id  

        orders = Order.objects.filter(requestStatus__in=["Accepted", "Order cancelled"], acceptedUser=accepted_user)
        serializer = OrderSerializerWithDistance(orders, many=True)
    except Exception as e:
        return Response({"details":e})    
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
        print("orders", orders)
        serializer = OrderSerializerWithDistance(orders, many=True)
    except:
        return Response({"details":"No Pending orders found"})    
    return Response(serializer.data)   


@api_view(['POST']) 
@permission_classes([IsAuthenticated]) 
def completeOrder(request, id):
    try:
        user = request.user
        data = request.data
        #order_items = data['orderItems']

        order = Order.objects.get(id=id)
        order.totalPrice = data['totalPrice']
        order.completedUser = user
        order.completedDate = datetime.today()
        order.requestStatus = "Completed"
        order.save()

        sell_request = SellRequest.objects.get(id=order.sellRequest.id)
        sell_request.requestStatus = "Completed"
        sell_request.save()

        for i in data['orderItems']:
            item = Item.objects.get(id=i['id'])
            OrderItem.objects.create(
                order=order,
                item=item,
                quantity=i['qty']
            )

  
            
        serializer = OrderSerializer(order, many=False)    
        return Response(serializer.data)
    except Exception as e:
        return Response(e)

@api_view(['PUT']) 
@permission_classes([IsAuthenticated]) 
def cancelOrder(request, id):
    try:
        user = request.user

        order = Order.objects.get(id=id)
        order.requestStatus = "Order cancelled"
        order.save()

        sell_request = SellRequest.objects.get(id=order.sellRequest.id)
        sell_request.requestStatus = "Requested"
        sell_request.save()

  
            
        serializer = OrderSerializer(order, many=False)    
        return Response(serializer.data)
    except Exception as e:
        return Response(e)


@api_view(['POST']) 
@permission_classes([IsAuthenticated]) 
def acceptSellRequest(request, id):
    try:
        user = request.user
        data = request.data
        sell_request = SellRequest.objects.get(id=id)
        print("date", data['pickupDate'])

        order = Order.objects.create(
            sellRequest=sell_request,
            requestStatus="Accepted",
            pickupDate=data['pickupDate'],
            acceptedUser=user,
            acceptedDate=datetime.today()
        )
        print("order: ",order)

        sell_request.requestStatus="Accepted"
        sell_request.save()
        
            
        serializer = SellRequestWithDistanceSerializer(sell_request, many=False, context={'user_id': user.id})    
        return Response(serializer.data)
    except Exception as e:
        return Response(e)

@api_view(['GET']) 
@permission_classes([IsAuthenticated]) 
def getOrdersToCompleteTodayForScraperStaff(request):
    try:
        user = request.user
        staff = ScraperStaffProfile.objects.get(staff__id=user.id)
        print("pooo", staff.staffOf.id)
        orders = Order.objects.filter(requestStatus="Accepted", acceptedUser=staff.staffOf.id)
        serializer = OrderSerializerWithDistance(orders, many=True, context={'user_id': staff.staffOf.id})    
        return Response(serializer.data)
    except Exception as e:
        print(e)
        return Response(e)


@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def getAllCategoryAndItems(request):
    try:
        category = Category.objects.all()
        serializer = CategorySerializerWithItems(category, many=True)
        return Response(serializer.data)
    except:
        return Response("No Category Found")     

# register normal user
@api_view(['POST'])    
def registerScrapSeller(request):
    data = request.data
    try:
        user = CustomUser.objects.create(
            first_name=data['name'],
            username=data['username'],
            password=make_password(data['password']),
            userType="ScrapSeller"
        )
        user.is_active=True
        user.save()
        serializer = UserSerializerWithToken(user, many=False)
    except:
        message = {'detail':'user with this username already exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)    
    return Response(serializer.data)    


@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def getAllReviews(request):
    try:
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    except:
        return Response("No Reviews Found") 


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
def createSellRequest(request):
    try:
        user = request.user
        data = request.data
        address = Address.objects.get(id=data['addressId'], user__id=user.id)
        sell_request = SellRequest.objects.create(
            pickupAddress=address,
            requestStatus="Requested",
            requestedUser=user,
        )
        for i in data['items']:
            item = Item.objects.get(id=i['id'])
            sell_request.items.add(item)

        serializer = SellRequestSerializer(sell_request, many=False)
        return Response(serializer.data)
    except:
        return Response("No Reviews Found") 


@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def getAllSellRequestOrders(request):
    try:
        user = request.user

        sell_requests = SellRequest.objects.filter(requestedUser__id=user.id)
        serializer = SellRequestSerializerWithOrder(sell_requests, many=True)
        return Response(serializer.data)
    except Exception as e:
        print("e", e)
        return Response({"error":e})   


@api_view(['POST', 'DELETE']) 
@permission_classes([IsAuthenticated])
def manageOrderReview(request, id):
    try:
        user = request.user
        data = request.data
        order = Order.objects.get(id=id)

        if request.method=='DELETE':
            review = Review.objects.get(order__id=order.id)
            review.delete()
        if request.method=='POST':
            review = Review.objects.create(
                order=order,
                reviewedUser=user,
                reviewText=data['review']
            )

        serializer = ReviewSerializer(review, many=False)
        return Response(serializer.data)
    except Exception as e:
        print("e", e)
        return Response({"error":e})  


@api_view(['PUT']) 
@permission_classes([IsAuthenticated])
def cancelSellRequest(request, id):
    try:
        user = request.user

        sell_request = SellRequest.objects.get(id=id)
        sell_request.requestStatus="Cancelled"
        sell_request.save()
        
        try:
            order = Order.objects.get(sellRequest__id=sell_request.id)
            order.requestStatus = "Request cancelled"
            order.save()
        except Order.DoesNotExist:
            pass


        serializer = SellRequestSerializerWithOrder(sell_request, many=False)
        return Response(serializer.data)
    except Exception as e:
        print("e", e)
        return Response({"error":e})     

@api_view(['GET', 'POST', 'PUT']) 
@permission_classes([IsAuthenticated])
def itemManagementForAdmin(request):
    if request.method == 'GET':
        items = Item.objects.all()
        serializer =  ItemSerializer(items, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        data = request.data
        category = Category.objects.get(id=data['categoryId'])
        item = Item.objects.create(
            itemName=data['itemName'],
            rate=data['rate'],
            category=category,
            unit=data['unit']
        )
        serializer =  ItemSerializer(item, many=False) 
        return Response(serializer.data)

    if request.method == "PUT":
        data = request.data

        item = Item.objects.get(id=data['itemId'])
        category = Category.objects.get(id=data['categoryId'])

        item.itemName=data['itemName'],
        item.rate=data['rate'],
        item.category=category,
        item.unit=data['unit'],
        item.save()
   
        serializer = ItemSerializer(item, many=False) 
        return Response(serializer.data)


@api_view(['GET', 'POST', 'PUT']) 
@permission_classes([IsAuthenticated])
def categoryManagementForAdmin(request):
    try:
        if request.method == 'GET':
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            data = request.data
            category = Category.objects.create(
                categoryName=data['categoryName'],
            )
            serializer =  CategorySerializer(category, many=False)
            return Response(serializer.data)

        if request.method == "PUT":
            data = request.data

            category = Category.objects.get(id=data['categoryId'])

            category.categoryName=data['categoryName'],
            category.save()
   
            serializer =  ItemSerializer(category, many=False) 
            return Response(serializer.data)
    except Category.DoesNotExist:
        return Response({"details":"No category Exist"})   


@api_view(['GET', 'PUT']) 
@permission_classes([IsAuthenticated])
def scrapBuyerAdminManagementForAdmin(request):
    try:
        if request.method=="GET":
            scraper_admin = CustomUser.objects.filter(userType="ScraperAdmin") 
            serializer = UserSerializerForScraperAdmin(scraper_admin, many=True)

        if request.method=="PUT":
            data = request.data
            user = CustomUser.objects.get(id=data['userId'])
            if user.is_active==True:
                user.is_active = False
            else:
                user.is_active = True

            user.save()
            serializer = UserSerializerForScraperAdmin(user, many=False)
            
        return Response(serializer.data)
    except CustomUser.DoesNotExist:
        return Response({"Details":"No user found"})

@api_view(['GET', 'PUT']) 
@permission_classes([IsAuthenticated])
def scrapBuyerStaffManagementForAdmin(request):
    try:
        if request.method=="GET":
            scraper_admin = CustomUser.objects.filter(userType="ScraperStaff") 
            serializer = UserSerializerForScraperStaff(scraper_admin, many=True)

        if request.method=="PUT":
            data = request.data
            user = CustomUser.objects.get(id=data['userId'])
            if user.is_active==True:
                user.is_active = False
            else:
                user.is_active = True
            user.save()
            serializer = UserSerializerForScraperStaff(user, many=False)
            
        return Response(serializer.data)
    except CustomUser.DoesNotExist:
        return Response({"Details":"No user found"})

@api_view(['GET', 'PUT']) 
@permission_classes([IsAuthenticated])
def scrapSellerManagementForAdmin(request):
    try:
        if request.method=="GET":
            scrap_seller = CustomUser.objects.filter(userType="ScrapSeller") 
            serializer = UserSerializerForScrapSeller(scrap_seller, many=True)

        if request.method=="PUT":
            data = request.data
            user = CustomUser.objects.get(id=data['userId'])
            if user.is_active==True:
                user.is_active = False
            else:
                user.is_active = True
            user.save()
            serializer = UserSerializerForScrapSeller(user, many=False)
            
        return Response(serializer.data)
    except CustomUser.DoesNotExist:
        return Response({"Details":"No user found"})

@api_view(['GET', 'PUT']) 
@permission_classes([IsAuthenticated])
def sellRequestManagementForAdmin(request):
    try:
        if request.method=="GET":
            sell_requests = SellRequest.objects.all()
            serializer = SellRequestSerializer(sell_requests, many=True)
            return Response(serializer.data)

        if request.method=="PUT":
            print("ooi1")
            data = request.data
            sell_request = SellRequest.objects.get(id=data['sellRequestId'])

            if sell_request.requestStatus=="Accepted":

                order = Order.objects.get(sellRequest__id=sell_request.id)
                order.requestStatus='Disabled'
                order.save()

                sell_request.requestStatus="Disabled"
                sell_request.save()
                serializer = SellRequestSerializer(sell_request, many=False)
                return Response(serializer.data)

            if sell_request.requestStatus=="Requested":
                sell_request.requestStatus="Disabled"
                sell_request.save()
                serializer = SellRequestSerializer(sell_request, many=False)
                return Response(serializer.data)

            if sell_request.requestStatus=="Disabled":
                try:
                    order = Order.objects.get(sellRequest__id=sell_request.id)
                    order.requestStatus = "Accepted"
                    order.save()

                    sell_request.requestStatus="Accepted"
                    sell_request.save()
                except Order.DoesNotExist:

                    sell_request.requestStatus="Requested"
                    sell_request.save()        

                serializer = SellRequestSerializer(sell_request, many=False)
                return Response(serializer.data)

    except SellRequest.DoesNotExist:
        return Response({"Details":"No order request found"}) 


@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def orderManagementForAdmin(request):
    try:
        if request.method=="GET":
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
            
        return Response(serializer.data)
    except SellRequest.DoesNotExist:
        return Response({"Details":"No order found"})  

@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def statsForAdmin(request):
    try:
        if request.method=="GET":
            orders = Order.objects.all()
            total_order_count = orders.count()
            now = datetime.now()
            seven_days_ago = datetime.now()-timedelta(days=7)

            orders_in_last_seven_days = Order.objects.filter(acceptedDate__range=[seven_days_ago, now])
            orders_in_last_seven_days_count = orders_in_last_seven_days.count()

            users = CustomUser.objects.all()
            total_users_count = users.count()

            newusers_in_last_seven_days = CustomUser.objects.filter(date_joined__range=[seven_days_ago, now])
            newusers_in_last_seven_days_count = newusers_in_last_seven_days.count()

            
        return Response({"totalOrders":total_order_count, "totalOrdersInLastSevenDays":orders_in_last_seven_days_count, "totalUsers":total_users_count, "totalUsersInlastSevenDays":newusers_in_last_seven_days_count})
    except SellRequest.DoesNotExist:
        return Response({"Details":"No order found"})
        


@api_view(['GET', 'POST', 'PUT', 'DELETE']) 
@permission_classes([IsAuthenticated])
def pickupAddressManagementForSeller(request): 
    user = request.user
    try:
        if request.method=="GET":
            addresses = Address.objects.filter(user__id=user.id)
            serializer = AddressSerializer(addresses, many=True)

        if request.method=="POST":
            data = request.data
    
            address = Address.objects.create(
                user=user,
                addressName=data['addressName'],
                city=data['city'],
                village=data['village'],
                district=data['district'],
                state=data['state'],
                postalCode=data['postalCode'],
                landmark=data['landmark'],
                houseOrFlatNo=data['houseOrFlatNo'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                phoneNumber=data['phoneNumber']
            )
            serializer = AddressSerializer(address, many=False)

        if request.method=="PUT":
            address_id = request.query_params.get('id', None)
            data = request.data
            address = Address.objects.get(id=address_id)

            address.addressName = data['addressName'],
            address.city=data['city'],
            address.village=data['village'],
            address.district=data['district'],
            address.state=data['state'],
            address.postalCode=data['postalCode'],
            address.landmark=data['landmark'],
            address.houseOrFlatNo=data['houseOrFlatNo'],
            address.phoneNumber=data['phoneNumber']

            address.save()
            serializer = AddressSerializer(address, many=False)
            
        if request.method=="DELETE":
            address_id = request.query_params.get('id', None)
            address = Address.objects.get(id=address_id)
            address.delete()
            serializer = AddressSerializer(address, many=False)    
 
        return Response(serializer.data)
    except SellRequest.DoesNotExist:
        return Response({"Details":"No order found"}) 


                                                      



     
