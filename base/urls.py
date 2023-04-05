
from webbrowser import get
from django.urls import path
from .views import MyTokenObtainPairView, registerScraper, createPickupAddresses, getAllSellRequestOrders, createSellRequest, getPickupAddresses, scraperAdminProfileCreator, addStaffToBusiness, getAllStaffs, deactivateStaff, getAllSellRequests, getAllTodaysSellRequests, getAllPendingOrders, getAllCompletedOrders, completeOrder, cancelOrder, acceptSellRequest, getOrdersToCompleteTodayForScraperStaff, getAllCategoryAndItems, registerScrapSeller, getAllReviews, manageOrderReview


urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/scraper/', registerScraper, name='registerScraper'),
    path('scraper/admin/profile-creator/<int:id>/', scraperAdminProfileCreator, name='scraperAdminProfileCreator'),
    path('scraper/admin/all-staffs/', getAllStaffs, name='getAllStaffs'),
    path('scraper/admin/deactivate-staff/<int:id>/', deactivateStaff, name='deactivateStaff'),
    path('scraper/staff/add-staff/<int:id>/', addStaffToBusiness, name='addStaffToBusiness'),
    path('scraper/staff/get-orders-to-complete-today/', getOrdersToCompleteTodayForScraperStaff, name='getOrdersToCompleteTodayForScraperStaff'),

    path('scraper/admin/sell-requests/', getAllSellRequests, name='getAllSellRequests'),
    path('scraper/admin/todays-sell-requests/', getAllTodaysSellRequests, name='getAllTodaysellRequests'),
    path('scraper/admin/pending-orders/', getAllPendingOrders, name='getAllPendingOrders'),
    path('scraper/admin/completed-orders/', getAllCompletedOrders, name='getAllCompletedOrders'),
    path('scraper/admin/complete-order/<int:id>/', completeOrder, name='completeOrder'),
    path('scraper/admin/cancel-order/<int:id>/', cancelOrder, name='cancelOrder'),
    path('scraper/admin/accept-sell-request/<int:id>/', acceptSellRequest, name='acceptSellRequest'),

    path('category/items/', getAllCategoryAndItems, name='getAllCategoryAndItems'),
    path('register/user/', registerScrapSeller, name='registerScrapSeller'),
    path('user/review/', getAllReviews, name='getAllReviews'),
    path('user/pickup-addresses/', getPickupAddresses, name='getPickupAddresses'),
    path('user/create-sell-request/', createSellRequest, name='createSellRequest'),
    path('user/create-pickup-address/', createPickupAddresses, name='createPickupAddresses'),
    path('user/sellrequest-orders/', getAllSellRequestOrders, name='getAllSellRequestOrders'),
    path('user/sellrequest-orders/manage-review/<int:id>/', manageOrderReview, name='createOrderReview'),


]
