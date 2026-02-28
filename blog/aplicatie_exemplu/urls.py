from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('log/',views.log,name="log"),
    path('index/',views.index,name="index"),
    path('contact/', views.contact,name='contact'),
    path('produs/',views.afiare_produse,name='produs'),
    path('cos_virtual/',views.cart_view,name='cos_virtual'),
    path('despre/',views.despre,name='despre'),
    path('produs/<int:id_produs>/',views.detalii_produs,name='detalii_produs'),
    path('produs/adauga/', views.adauga_produs, name='adauga_produs'),
    path('inregistrare/', views.inregistrare_utilizator, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('schimbare-parola/', auth_views.PasswordChangeView.as_view(
        template_name='aplicatie_exemplu/schimbare_parola.html',
        success_url='/profil/'
    ), name='password_change'),
    path('profil/', views.profil_view, name='profil'),
    path('email_confirmare/<str:cod>/', views.email_confirmare, name='email_confirmare'),
    path('cart/', views.cart_view, name='cart'),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)