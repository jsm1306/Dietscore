from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10) 
 

    def __str__(self):
        return self.name

class BMICalculation(models.Model):
    weight = models.FloatField()
    height = models.FloatField()
    bmi_value = models.FloatField()
    gender = models.CharField(max_length=10)
    category = models.CharField(max_length=100,default=0)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BMI: {self.bmi_value}"


class UserSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.username if self.user else 'Unknown'} at {self.submitted_at}"

class NutritionInfo(models.Model):
    item_name = models.CharField(max_length=100, unique=True)
    calories = models.FloatField()
    proteins = models.FloatField()
    fats = models.FloatField()
    sodium = models.FloatField(default=0)
    fiber = models.FloatField(default=0)
    carbs = models.FloatField()
    sugar = models.FloatField(default=0)
    category = models.ForeignKey(Category, related_name='nutrition_items', on_delete=models.CASCADE, null=True)
    price = models.FloatField(default=0)
    image = models.ImageField(upload_to='nutrition_images/', null=True, blank=True)
    is_weight_based = models.BooleanField(default=True)


    def __str__(self):
        return self.item_name

class ItemEntry(models.Model):
    submission = models.ForeignKey(UserSubmission, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    quantity = models.FloatField()
    calories = models.FloatField()
    proteins = models.FloatField()
    fats = models.FloatField()
    sodium = models.FloatField(default=0)
    fiber = models.FloatField(default=0)
    carbs = models.FloatField()
    sugar = models.FloatField(default=0)
    category = models.ForeignKey(Category, related_name='item_entries', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.item_name} - {self.quantity}g"
