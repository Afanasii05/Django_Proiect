from django.contrib import admin
from .models import Jucarie, Categorie, Furnizor, Oferta, EvenimentPromotional

class JucarieAdmin(admin.ModelAdmin):
    list_display = ('nume' ,'pret', 'marime','stoc')
    list_filter = ['pret']
    ordering = ['pret','marime']
    search_fields = ('nume','pret')
    fieldsets =(
        ('Info Generale',{
            'fields':('nume','pret','marime','stoc','poza')
        }),
        (
            'Detalii',{
                'fields':('descriere',),
                'classes':('collapse',),
            }
        ),
    )
    list_per_page = 5
    
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('id_jucarie', 'procent_reducere')
    search_fields = ('id_jucari','data_inceput')

class FurnizorAdmin(admin.ModelAdmin):
    list_display=('nume','telefon','email')
    search_fields =('nume','telefon','email')
    
class CategorieAdmin(admin.ModelAdmin):
    list_display=('nume','descriere')
    search_fields = ('nume','descriere')

class EvenimentPromotionalAdmin(admin.ModelAdmin):
    list_display =('nume','data_inceput')
    search_fields = ('nume','id_jucarie')


# Register your models here.
admin.site.register(Jucarie, JucarieAdmin)
admin.site.register(Categorie,CategorieAdmin)
admin.site.register(Furnizor, FurnizorAdmin)
admin.site.register(Oferta, OfertaAdmin)
admin.site.register(EvenimentPromotional, EvenimentPromotionalAdmin)

admin.site.site_header = "Panou de Administrare Site"
admin.site.site_title = "Admin Site"
admin.site.index_title = "Bine ai venit în panoul de administrare"