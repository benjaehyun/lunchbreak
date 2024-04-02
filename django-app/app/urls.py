from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import FoodView, GroupViewSet, UserCreateView, logout_view, csrf_token, change_user_name, get_restaurants_for_day
from .views import CustomTokenObtainPairView, CustomTokenRefreshView

router = DefaultRouter()
router.register(r'foods', FoodView)
router.register(r'groups', GroupViewSet)

# router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('userinfo/', views.get_user_info, name='user_info'),
    path('signup/', UserCreateView.as_view(), name='user_signup'),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),
    path('csrf/', csrf_token, name='csrf_token'),
    path('change-name/', change_user_name, name='change_name'),
    # path('orders/<int:employee_id>/', OrderDetailView.as_view(), name='order-detail'),
    # path('employee/<int:employee_id>/daily-orders/',
    #      EmployeeDailyOrdersView.as_view(), name='employee-daily-orders'),
    # Build out url for restaurants,
    path('restaurants/day/<str:date_str>/',
         get_restaurants_for_day, name='get_restaurants_for_day'),


]


# path('api/user-permissions/', views.UserGroupPermissionView.as_view(), name='user-permissions'),
