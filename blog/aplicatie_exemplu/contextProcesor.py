from .models import Categorie 
from .utilFunctions import  get_ip
def menu_categories(request):
    categorii_meniu = Categorie.objects.all()
    ip = get_ip(request)
    return {'categorii_meniu': categorii_meniu, 'ip_client': ip}