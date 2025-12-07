from .models import Categorie 

def menu_categories(request):
    categorii_meniu = Categorie.objects.all()
    return {'categorii_meniu': categorii_meniu}