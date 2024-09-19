from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(BMICalculation)
admin.site.register(UserSubmission)
admin.site.register(ItemEntry)
admin.site.register(NutritionInfo)
admin.site.register(Category)


