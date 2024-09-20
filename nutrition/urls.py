from django.urls import path
from . import views
urlpatterns=[
    path('',views.mains,name='mains'),
    path('add',views.add,name='add'),
    path('bmicalc',views.bmicalc,name='bmicalc'),
    path('score', views.score, name='score'), 
    path('compute/', views.compute, name='compute'),
    path('category-wise-items/', views.category_wise_items, name='category-wise-items'),
    # path('dropdown/', views.dropdown, name='dropdown'),
    path('categorize/', views.categorize, name='categorize'),
    path('suggester/', views.suggester, name='suggester'),
    # path('chart/', views.viewgraphs, name='viewgraphs'),

]