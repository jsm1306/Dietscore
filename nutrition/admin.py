from django.contrib import admin
from .models import UserProfile, BMICalculation, UserSubmission, ItemEntry, NutritionInfo

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(BMICalculation)
admin.site.register(UserSubmission)
admin.site.register(ItemEntry)
admin.site.register(NutritionInfo)

