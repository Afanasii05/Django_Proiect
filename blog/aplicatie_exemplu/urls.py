from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('info/', views.info, name='info'),
    path('log/',views.log,name="log"),
    path('index/',views.index,name="index"),
    path('contact/', views.in_lucru,name='contact'),
    path('produs',views.in_lucru,name='produs'),
    path('cos_virtual/',views.in_lucru,name='cos_virtual'),
    path('despre/',views.despre,name='despre'),
    
    
]   