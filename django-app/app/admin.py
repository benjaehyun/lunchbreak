from django.contrib import admin
from .models import Food, Restaurant, Category, MenuItem, Option, OptionValue, Day


# Register your models here.


admin.site.register(Food)
admin.site.register(Restaurant)
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Option)
admin.site.register(OptionValue)
admin.site.register(Day)
