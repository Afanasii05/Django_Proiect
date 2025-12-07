from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('info/', views.info, name='info'),
    path('log/',views.log,name="log"),
    path('index/',views.index,name="index"),
    path('contact/', views.in_lucru,name='contact'),
    path('produs/',views.afiare_produse,name='produs'),
    path('cos_virtual/',views.in_lucru,name='cos_virtual'),
    path('despre/',views.despre,name='despre'),
    path('produs/<int:id_produs>/',views.detalii_produs,name='detalii_produs'),
    path('produs/<str:categorie>/',views.afiare_produse,name='produs_categorie'),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)