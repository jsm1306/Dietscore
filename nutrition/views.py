from django.shortcuts import render, redirect
import requests
from django.conf import settings
from .models import UserProfile, BMICalculation, UserSubmission, ItemEntry, NutritionInfo, Category

def mains(request):
    return render(request,'mains.html',{'result':'Diet Score'})


def category_wise_items(request):
    categories = Category.objects.all()
    items_by_category = {category.name: NutritionInfo.objects.filter(category=category) for category in categories}
    
    context = {
        'items_by_category': items_by_category
    }
    return render(request, 'categorylist.html', context)

def add(request):
    if request.method == 'POST':
        name = str(request.POST['name'])
        age = int(request.POST['age'])
        gender = request.POST.get('options', '')
        request.session['name'] = name
        request.session['age'] = age
        request.session['gender'] = gender
        
        UserProfile.objects.create(name=name, age=age, gender=gender)

        nutrition_items = NutritionInfo.objects.values_list('item_name', flat=True)
        # categories = Category.objects.all()  
        
        return render(request, 'score.html', {
            'age': age,
            'name': name,
            'gender': gender,
            'nutrition_items': nutrition_items,
            # 'categories': categories  
        })
    return render(request, 'mains.html') 
def categorize(request):
    
    items_by_category = {}
    categories = Category.objects.all()  
    for category in categories:
        items = NutritionInfo.objects.filter(category=category)  
        items_by_category[category.name] = items 

    context = {
        'items_by_category': items_by_category
    }
    return render(request, 'selectcategories.html', context)
def suggester(request):
    if request.method == 'POST':
        items_by_category = {}
        categories = Category.objects.all()

        for category in categories:
            items = request.POST.getlist(f'item_{category.name}[]')
            items_by_category[category.name] = zip(items)

        context = {
            'items_by_category': items_by_category
        }
        return render(request, 'suggestresult.html', context)

def score(request):
    name = request.session.get('name')  
    age = request.session.get('age')     
    nutrition_items = NutritionInfo.objects.values_list('item_name', flat=True)

    return render(request, 'score.html', {
        'name': name,
        'age': age,
        'nutrition_items': nutrition_items,
    })

def bmicalc(request):
    if request.method == "POST":
        weight = int(request.POST.get('weig', 0))
        height = int(request.POST.get('heig', 0))
        age = int(request.POST.get('age', 0))
        gender = request.POST.get('options', '')

        if height == 0:
            error_message = "Height cannot be zero. Please enter a valid height."
            return render(request, 'bmiresult.html', {'error': error_message, 'age': age, 'gender': gender})

        ht = height / 100
        val3 = weight / (ht ** 2)
        
        if val3 < 18.5:
            res = "Underweight"
        elif 18.5 <= val3 < 24.9:
            res = "Normal weight"
        elif 25 <= val3 < 29.9:
            res = "Overweight"
        elif 30 <= val3 < 34.9:
            res = "Obesity Class 1"
        elif 35 <= val3 < 39.9:
            res = "Obesity Class 2"
        elif val3 >= 40:
            res = "Obesity Class 3"
        else:
            res = "Invalid BMI"

        BMICalculation.objects.create(weight=weight, height=height, bmi_value=val3, gender=gender, category=res)

        return render(request, 'bmiresult.html', {'result': round(val3), 'age': age, 'gender': gender, 'category': res})
    return render(request, 'bmical.html')

def daily(request):
    age = request.session.get('age')
    gender = request.session.get('gender')

    print(f"Calculating requirements for Age: {age}, Gender: {gender}")

    DAILY_REQUIREMENTS = {
        'Female': {
            (4, 8):  {'Calories': 1200, 'Proteins': 19, 'Fats': 70, 'Sodium': 2300, 'Fiber': 25, 'Carbs': 260, 'Sugar': 50},
            (9, 13): {'Calories': 1600, 'Proteins': 34, 'Fats': 70, 'Sodium': 2300, 'Fiber': 26, 'Carbs': 290, 'Sugar': 50},
            (14, 18): {'Calories': 1800, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 26, 'Carbs': 300, 'Sugar': 50},
            (19, 30): {'Calories': 2000, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 28, 'Carbs': 310, 'Sugar': 50},
            (31, 50): {'Calories': 1800, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 28, 'Carbs': 300, 'Sugar': 50},
            (51, 70): {'Calories': 1600, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 28, 'Carbs': 260, 'Sugar': 50},
            (71, 100): {'Calories': 1500, 'Proteins': 46, 'Fats': 70, 'Sodium': 2300, 'Fiber': 28, 'Carbs': 250, 'Sugar': 50},
        },
        'Male': {
            (4, 8):  {'Calories': 1400, 'Proteins': 19, 'Fats': 70, 'Sodium': 2300, 'Fiber': 25, 'Carbs': 270, 'Sugar': 50},
            (9, 13): {'Calories': 1800, 'Proteins': 34, 'Fats': 70, 'Sodium': 2300, 'Fiber': 31, 'Carbs': 300, 'Sugar': 50},
            (14, 18): {'Calories': 2200, 'Proteins': 52, 'Fats': 70, 'Sodium': 2300, 'Fiber': 31, 'Carbs': 320, 'Sugar': 50},
            (19, 30): {'Calories': 2400, 'Proteins': 56, 'Fats': 70, 'Sodium': 2300, 'Fiber': 34, 'Carbs': 330, 'Sugar': 50},
            (31, 50): {'Calories': 2200, 'Proteins': 56, 'Fats': 70, 'Sodium': 2300, 'Fiber': 34, 'Carbs': 300, 'Sugar': 50},
            (51, 70): {'Calories': 2000, 'Proteins': 56, 'Fats': 70, 'Sodium': 2300, 'Fiber': 30, 'Carbs': 280, 'Sugar': 50},
            (71, 100): {'Calories': 1800, 'Proteins': 56, 'Fats': 70, 'Sodium': 2300, 'Fiber': 30, 'Carbs': 250, 'Sugar': 50},
        }
    }
    for age_range, requirements in DAILY_REQUIREMENTS.get(gender, {}).items():
        if age_range[0] <= age <= age_range[1]:
            print(f"Requirements found: {requirements}")
            return requirements

    print("No matching requirements found")
    return {}  

def load_nutrition_data():
    nutrition_data = {}
    nutition_items = NutritionInfo.objects.all()
    
    for item in nutition_items:
        nutrition_data[item.item_name.lower()] = {
            'Calories': item.calories,
            'Proteins': item.proteins,
            'Fats': item.fats,
            'Sodium': item.sodium,
            'Fiber': item.fiber,
            'Carbs': item.carbs,
            'Sugar': item.sugar
        }
    return nutrition_data

def compute(request):
    if request.method == 'POST':
        items = request.POST.getlist('item[]')
        quantities = request.POST.getlist('quantity[]')

        nutrition_data = load_nutrition_data()
        requirements = daily(request)

        if not requirements:
            print("Requirements not found, setting defaults.")
            requirements = {'Calories': 0, 'Proteins': 0, 'Fats': 0, 'Sodium': 0, 'Fiber': 0, 'Carbs': 0, 'Sugar': 0}

        totals = {'Calories': 0, 'Proteins': 0, 'Fats': 0, 'Sodium': 0, 'Fiber': 0, 'Carbs': 0, 'Sugar': 0}
        item_details = []

        submission = UserSubmission.objects.create()

        for item, quantity in zip(items, quantities):
            item = item.lower().strip()
            try:
                quantity = float(quantity)
                if item in nutrition_data:
                    item_info = nutrition_data[item]
                    for key in totals:
                        totals[key] += (item_info[key] * quantity / 100)
                        totals[key] = round(totals[key], 2)
                    item_details.append((item, quantity, item_info))

                    ItemEntry.objects.create(
                        submission=submission,
                        item_name=item,
                        quantity=quantity,
                        calories=item_info['Calories'] * quantity / 100,
                        proteins=item_info['Proteins'] * quantity / 100,
                        fats=item_info['Fats'] * quantity / 100,
                        sodium=item_info['Sodium'] * quantity / 100,
                        fiber=item_info['Fiber'] * quantity / 100,
                        carbs=item_info['Carbs'] * quantity / 100,
                        sugar=item_info['Sugar'] * quantity / 100
                    )
            except ValueError:
                print(f"Error processing item: {item}, quantity: {quantity}")

        meets_requirements = {key: totals[key] >= requirements[key] for key in totals}

        context = {
            'item_details': item_details,
            'totals': totals,
            'meets_requirements': meets_requirements,
            'requirement': requirements
        }
        return render(request, 'inputsbase.html', context)

    return render(request, 'score.html')