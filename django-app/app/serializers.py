from rest_framework import serializers
from .models import Food, Order, OrderItem, Restaurant, Day
from django.contrib.auth.models import User, Group


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ('title', 'description', 'completed')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'groups']

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserFirstNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name']  # Targeting the 'first_name' field

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.save()
        return instance


# class RestaurantSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Restaurant
#         fields = '__all__'

class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = ['day', 'get_day_display']

class RestaurantSerializer(serializers.ModelSerializer):
    active_days = DaySerializer(many=True, read_only=True)
    
    class Meta:
        model = Restaurant
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'selected_options']


class OrderSerializer(serializers.ModelSerializer):
    menu_items = OrderItemSerializer(source='orderitem_set', many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'company', 'restaurant', 'menu_items',
                  'order_date', 'total_price', 'status', 'special_instructions']
