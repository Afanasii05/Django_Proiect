import uuid
from django.db import models

# Create your models here.

class Jucarie(models.Model):
    id_jucarie = models.PositiveIntegerField(primary_key=True,editable=False)
    nume_categorie = models.ForeignKey('Categorie',on_delete=models.CASCADE,null=True)
    nume = models.CharField(max_length=100)
    descriere = models.TextField(null=True)
    pret = models.DecimalField(max_digits=5, decimal_places=2)
    class marimeChoices(models.TextChoices):
        MICA = 'S', ('Mica')
        MEDIE = 'M', ('Medie')
        MARE = 'L', ('Mare')
    marime = models.CharField(choices=marimeChoices.choices, max_length=1, default=marimeChoices.MICA)
    stoc = models.PositiveIntegerField(default=0)
    data_adaugare = models.DateField(auto_now_add=True)
    poza = models.ImageField(upload_to='data_base_images/jucarii', null=True, blank=True)
    def __str__(self):
        return self.nume
    
class Categorie(models.Model):
    nume = models.CharField(primary_key=True,max_length=50, unique=True)
    descriere = models.TextField(null=True)
    def __str__(self):
        return self.nume
    
class Furnizor(models.Model):
    id_furnizor = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nume = models.CharField(max_length=100)
    biografie = models.TextField(null=True)
    telefon = models.CharField(max_length=15)
    email = models.EmailField()
    poza = models.ImageField(upload_to='data_base_images/furnizori', null=True, blank=True)
    def __str__(self):
        return self.nume
    
class Oferta(models.Model):
    id_oferta = models.AutoField(primary_key=True)
    id_jucarie = models.ForeignKey(Jucarie, on_delete=models.CASCADE)
    procent_reducere = models.DecimalField(max_digits=4, decimal_places=2)
    data_inceput = models.DateField()
    data_sfarsit = models.DateField()
    activa = models.BooleanField(default=True)
    def __str__(self):
        return f"Oferta pentru {self.jucarie.nume}: {self.procent_reducere}% reducere"
class EvenimentPromotional(models.Model):
    id_eveniment = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100)
    Detalii = models.TextField(null=True)
    id_jucarie = models.ManyToManyField(Jucarie)
    data_inceput = models.DateField()
    data_sfarsit = models.DateField()
    def __str__(self):
        return self.nume