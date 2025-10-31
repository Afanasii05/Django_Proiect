from django.contrib import admin
from .models import Jucarie, Categorie, Furnizor, Oferta, EvenimentPromotional
# Register your models here.
admin.site.register(Jucarie)
admin.site.register(Categorie)
admin.site.register(Furnizor)
admin.site.register(Oferta)
admin.site.register(EvenimentPromotional)