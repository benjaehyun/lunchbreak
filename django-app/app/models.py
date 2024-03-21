from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.
class Food(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    completed = models.BooleanField(default=False)

    def _str_(self):
        return self.title

    
class Company(models.Model):
    company_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    delivery_instructions = models.TextField(blank=True, null=True)
    budget_periodicity = models.CharField(max_length=50, default='monthly')
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name
    
class Day(models.Model):
    DAY_CHOICES = [
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    ]
    day = models.IntegerField(choices=DAY_CHOICES, unique=True)

    def __str__(self):
        return self.get_day_display()

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20)  # Assuming international format might be used
    active_days = models.ManyToManyField(Day, related_name='restaurants')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='categories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('restaurant', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='menu_items', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='menu_items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Option(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    is_required = models.BooleanField(default=False)
    allow_multiple = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

class OptionValue(models.Model):
    option = models.ForeignKey(Option, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    additional_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.option.name} - {self.value}"

    
class Order(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    menu_items = models.ManyToManyField(MenuItem, through='OrderItem', related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    budget_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    charged_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    special_instructions = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.charged_amount = max(self.total_price - self.budget_deduction, 0)  # Ensure charged_amount cannot be negative
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.pk} - {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(OptionValue, related_name='order_items', blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
    

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles')

    def __str__(self):
        return self.user.username