from django.shortcuts import render, redirect
import requests
from django.conf import settings
from .models import *
from scipy.optimize import linprog
import numpy as np
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def registerPage(request):
        form=UserCreationForm()
        if request.method=="POST":
            form=UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')
            else:
                messages.error(request,"Password does not follow the rules")
        context={'form':form}
        return render(request, 'register.html', context)
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('mains')
    else:
        if request.method=='POST':
            username=request.POST.get('username')
            password=request.POST.get('password')
            print(username, password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('mains')
            else:
                messages.success(request,"Username or Password is incorrect")
    return render(request,'login.html')


@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def mains(request):#dummy
    return render(request,'mains.html',{'result':'Diet Score'})

@login_required(login_url='login')
def category_wise_items(request):#to display categories in category.html(navbar)
    categories = Category.objects.all()
    items_by_category = {category.name: NutritionInfo.objects.filter(category=category) for category in categories}
    
    context = {
        'items_by_category': items_by_category
    }
    return render(request, 'categorylist.html', context)
@login_required(login_url='login')
def add(request):#inputs display fn
    if request.method=='POST':
        name=str(request.POST['name'])
        age=int(request.POST['age'])
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

@login_required(login_url='login')
def categorize(request):#to display items category wise
    items_by_category = {}
    categories = Category.objects.all()  
    for category in categories:
        items = NutritionInfo.objects.filter(category=category)  
        items_by_category[category.name] = items 
    context = {
        'items_by_category': items_by_category
    }
    return render(request, 'selectcategories.html', context)

@login_required(login_url='login')
def suggester(request):
    if request.method == "POST":
        selected_items = []
        for category, items in request.POST.items():
            if category.startswith('item_'):
                selected_items.append(items)  
        
        nutrition_data = []
        for item_name in selected_items:
            item = NutritionInfo.objects.get(item_name=item_name)
            nutrition_data.append(item)
            print(f"Item: {item.item_name}, Calories: {item.calories}, Proteins: {item.proteins}, Fats: {item.fats}, Sodium: {item.sodium},Fiber: {item.fiber},Carbs: {item.carbs},Sugar: {item.sugar},Price: {item.price}")

        requirements = daily(request)
        
        calories = [-item.calories for item in nutrition_data]
        proteins = [-item.proteins for item in nutrition_data]
        fats = [-item.fats for item in nutrition_data]
        sodium = [-item.sodium for item in nutrition_data]
        fiber = [-item.fiber for item in nutrition_data]
        carbs = [-item.carbs for item in nutrition_data]
        sugar = [-item.sugar for item in nutrition_data]
        
        c = [item.price for item in nutrition_data]
        
        A = [calories, proteins, fats,sodium,fiber,carbs,sugar]
        
        b = [-requirements['Calories'], -requirements['Proteins'], -requirements['Fats'],
            -requirements['Sodium'], -requirements['Fiber'], -requirements['Carbs'] , -requirements['Sugar']   ]

        x_bounds = [(0, None) for _ in selected_items] 
        res = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds, options={"disp": True})
        
        quantities = res.x  
        
        results = [(item.item_name, quantity) for item, quantity in zip(nutrition_data, quantities)]
        
        return render(request, 'suggestresult.html', {'results': results})
    
    return redirect('mains.html')

@login_required(login_url='login')
def score(request):#back button fn in inputsbase.html
    name = request.session.get('name')  
    age = request.session.get('age')     
    nutrition_items = NutritionInfo.objects.values_list('item_name', flat=True)
    return render(request, 'score.html', {
        'name': name,
        'age': age,
        'nutrition_items': nutrition_items,
    })
@login_required(login_url='login')
def bmicalc(request):#bmi calculator
    if request.method == "POST":
        weight = int(request.POST.get('weig', 0))
        height = int(request.POST.get('heig', 0))
        age = int(request.POST.get('age', 0))
        gender = request.POST.get('options', '')
        if height==0 or weight==0:
            errormsg="Height/Weight cannot be zero. Please enter valid height."
            return render(request, 'bmiresult.html', {'error': errormsg, 'age': age, 'gender': gender})
        if age<0 or age >100:
            errormsg="Invalid age."
            return render(request, 'bmiresult.html', {'error': errormsg, 'age': age, 'gender': gender})
        ht = height/100
        val3 = weight/(ht**2)
        if val3 < 18.5:
            res = "Underweight"
        elif 18.5 <= val3 < 25:
            res = "Normal weight"
        elif 25 <= val3 <= 29.9:
            res = "Overweight"
        elif 30 <= val3 <= 34.9:
            res = "Obesity Class 1"
        elif 35 <= val3 <= 39.9:
            res = "Obesity Class 2"
        elif val3 >= 40:
            res = "Obesity Class 3"
        else:
            res = "Invalid BMI"
        BMICalculation.objects.create(weight=weight, height=height, bmi_value=val3, gender=gender, category=res)
        return render(request, 'bmiresult.html', {'result': round(val3), 'age': age, 'gender': gender, 'category': res})
    return render(request, 'bmical.html')
@login_required(login_url='login')
def daily(request):#this fn is to determine the min requirements based on age&gender, use in compute fn
    age = request.session.get('age')
    gender = request.session.get('gender')
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
            return requirements
    return {}  

def load_nutrition_data():# this fn is to load the nutrition data of items and use in compute fn
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


def compute(request):#**** fn, to calculate req met or not, sum divide and compare
    if request.method == 'POST':
        items = request.POST.getlist('item[]')
        quantities = request.POST.getlist('quantity[]')
        nutrition_data = load_nutrition_data()
        requirements = daily(request)

        if not requirements:
            print("Error1-not found")
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
                    ItemEntry.objects.create(#to edit items entered by user in database
                        submission=submission,
                        item_name=item,
                        quantity=quantity,
                        calories=item_info['Calories']*quantity/100,
                        proteins=item_info['Proteins']*quantity/100,
                        fats=item_info['Fats']*quantity/100,
                        sodium=item_info['Sodium']*quantity/100,
                        fiber=item_info['Fiber']*quantity/100,
                        carbs=item_info['Carbs']*quantity/100,
                        sugar=item_info['Sugar']*quantity/100
                    )
            except ValueError:
                print("Error2-cant fetch")#print in console
         #comparing calculated nutrition with min req
        meets_requirements = {key: totals[key] >= requirements[key] for key in totals}
        request.session['totals'] = totals
        context = {
            'item_details': item_details,
            'totals': totals,
            'meets_requirements': meets_requirements,
            'requirement': requirements
        }
        return render(request,'inputsbase.html',context)

    return render(request,'score.html')
'''
Changes to be made: 
● Qunatity measures to be added: in (g), in packet, in millilitres, number(in tiffin)
● Check calories
● Sweets combine in main course
● Include 3/4 items in main course while selecting for recommendation 
● Add images to items
● Quantity measure from number to grams
● YES in green NO in red
● Dietscore logo
'''
