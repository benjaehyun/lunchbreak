from django.shortcuts import render
from rest_framework import viewsets
from .serializers import FoodSerializer, GroupSerializer, UserSerializer, UserRegistrationSerializer, UserFirstNameSerializer
from .models import Food
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
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

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
            response = Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
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


# class CustomTokenObtainPairView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)

#         try:
#             serializer.is_valid(raise_exception=True)
#         except Exception as e:
#             return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

#         data = serializer.validated_data
#         response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
#         response.set_cookie(
#             'access_token',
#             data['access'],
#             httponly=True,
#             max_age=3600,  # or your desired duration
#             samesite='Lax',
#             secure=True,  # Use secure=True in production
#             path='/',
#         )
#         response.set_cookie(
#             'refresh_token',
#             data['refresh'],
#             httponly=True,
#             max_age=86400,  # or your desired duration
#             samesite='Lax',
#             secure=True,
#             path='/',
#         )
#         return response


# @method_decorator(csrf_protect, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:  # Token created successfully
            access_token = response.data['access']
            refresh_token = response.data['refresh']
            response.set_cookie(
                'access_token', access_token, httponly=True, max_age=3600, samesite='Lax'
            )
            response.set_cookie(
                'refresh_token', refresh_token, httponly=True, samesite='Lax'
            )
            # del response.data['refresh']  # Optional: Remove refresh token from response
        return response

    
# class CustomTokenRefreshView(TokenRefreshView):
#     def post(self, request, *args, **kwargs):
#         # Extract refresh token from cookies instead of request data
#         refresh_token = request.COOKIES.get('refresh_token')
#         if not refresh_token:
#             return Response({"detail": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = self.get_serializer(data={'refresh': refresh_token})

#         try:
#             serializer.is_valid(raise_exception=True)
#         except Exception as e:
#             return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

#         data = serializer.validated_data
#         response = Response({"message": "Token refreshed successfully"}, status=status.HTTP_200_OK)
#         response.set_cookie(
#             'access_token',
#             data['access'],
#             httponly=True,
#             max_age=3600,
#             samesite='Lax',
#             secure=True,  # Consider toggling based on settings.DEBUG for testing
#             path='/',
#         )
#         return response

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Set the refresh token from cookies to the request data
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