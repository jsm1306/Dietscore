from django.urls import path
from . import views
urlpatterns=[
    path('',views.mains,name='mains'),
    path('add',views.add,name='add'),
    path('bmicalc',views.bmicalc,name='bmicalc'),
    path('score/', views.score, name='score'), 
    path('compute/', views.compute, name='compute'),
    
]