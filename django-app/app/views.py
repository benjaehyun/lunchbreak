from django.shortcuts import render
from rest_framework import viewsets
from .serializers import RestaurantSerializer, FoodSerializer, GroupSerializer, UserSerializer, UserRegistrationSerializer, UserFirstNameSerializer, OrderSerializer
from .models import Food, Order, OrderItem, Restaurant, Day
from django.contrib.auth.models import Group, User
from django.contrib.auth import logout, get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import CheckGroup
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
import logging
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework.generics import ListAPIView


logger = logging.getLogger(__name__)

# Create your views here.


class FoodView(viewsets.ModelViewSet):
    serializer_class = FoodSerializer
    queryset = Food.objects.all()
    # permission_classes = [check_group('Restaurant_Admin')]
    permission_classes = [CheckGroup.for_group('Restaurant_Admin')]


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        # logger.info(f"Received Signup Request: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            response = Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED)
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                max_age=3600,  # Adjust as needed
                samesite='Lax',
                secure=True,  # Set to False if not using HTTPS locally
                path='/',
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                max_age=86400,  # Adjust as needed
                samesite='Lax',
                secure=True,  # Set to False if not using HTTPS locally
                path='/',
            )
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    logger.info(request.COOKIES)
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


# @method_decorator(csrf_protect, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:  # Token created successfully
            access_token = response.data['access']
            refresh_token = response.data['refresh']
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                max_age=3600,
                samesite='Lax'
            )
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                samesite='Lax'
            )
            # del response.data['refresh']  # If we want to remove refresh token from response
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        request.data['refresh'] = request.COOKIES.get('refresh_token')
        try:
            # Attempt to refresh the token using the parent class's logic
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                # If token refresh is successful, update the access token cookie
                access_token = response.data['access']
                response.set_cookie(
                    'access_token', access_token, httponly=True, samesite='Lax'
                )
            return response

        except Exception as e:
            # Handle specific exceptions here as needed
            # For a generic catch-all, return a custom error response
            return Response({
                "error": "refresh_token_expired",
                "detail": "The refresh token is expired or invalid. Please login again."
            }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    response = JsonResponse({'message': 'Logout successful'})
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/')
    response.delete_cookie('csrftoken', path='/')
    return response


def csrf_token(request):
    # Ensure a CSRF token is set in the cookies
    csrf_token = get_token(request)
    return JsonResponse({'detail': 'CSRF token set in cookies'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_protect
def change_user_name(request):
    user = request.user
    serializer = UserFirstNameSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'First name updated successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDailyOrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view returns a list of all the orders placed by a given employee on a specific day.
        """
        employee_id = self.kwargs.get('employee_id')
        order_date = self.request.query_params.get('date')

        # Parse the date string to a date object (consider error handling for invalid formats)
        try:
            order_date = timezone.datetime.strptime(
                order_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Handle error or default to today's date
            order_date = timezone.now().date()

        # Filter orders by employee and date
        start_day = timezone.datetime.combine(
            order_date, timezone.datetime.min.time())
        end_day = timezone.datetime.combine(
            order_date, timezone.datetime.max.time())
        queryset = Order.objects.filter(
            user_id=employee_id, order_date__range=(start_day, end_day))

        return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_restaurants_for_day(request, date_str):
    if date_str:
        try:

            day_date = datetime.fromisoformat(date_str)
            weekday = day_date.isoweekday()
            day_instance = Day.objects.get(day=weekday)
            restaurants = Restaurant.objects.filter(active_days=day_instance)
            if restaurants.exists():

                serializer = RestaurantSerializer(restaurants, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response([], {'error': 'No restaurants found for this day'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': f'Incorrect date format: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        # except:
        #     # handling for incorrect date format
        #     return Response({'error': 'Incorrect date format'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    # If there's nothing to return, return an error or Empty array on frontend
