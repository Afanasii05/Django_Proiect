import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ValidationError


def validate_telefon(numar):
    if not numar.isdigit() or len(numar) < 7 or len(numar) > 15:
        raise ValidationError("Numarul de telefon trebuie sa contina doar cifre si sa aiba intre 7 si 15 cifre.")
def validate_email(email):
    if "@" not in email or "." not in email.split("@")[-1] or email[-1]=='.' or email[0]=='@':
        raise ValidationError("Adresa de email nu este valida.")
def validare_nume(nume):
    if len(nume) < 2 or len(nume) > 30 or not nume.replace(' ','').isalpha():
        raise ValidationError("Numele trebuie sa aiba intre 2 si 30 caractere si sa contina doar litere si spatii.")
# Create your models here.

class Jucarie(models.Model):
    nume_categorie = models.ForeignKey('Categorie',on_delete=models.CASCADE,null=True)
    nume = models.CharField(max_length=100)
    descriere = models.TextField(blank=True, null=True)
    pret = models.DecimalField(max_digits=5, decimal_places=2,validators=[MinValueValidator(1, message="Pretul trebuie sa fie cel putin 1 leu.")])
    class marimeChoices(models.TextChoices):
        MICA = 'S', ('Mica')
        MEDIE = 'M', ('Medie')
        MARE = 'L', ('Mare')
    marime = models.CharField(choices=marimeChoices.choices, max_length=1, default=marimeChoices.MICA)
    stoc = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0, message="Stocul nu poate fi negativ.")])
    data_adaugare = models.DateField(auto_now_add=True)
    poza = models.ImageField(upload_to='data_base_images/jucarii', null=True, blank=True)
    def __str__(self):
        return self.nume
    
class Categorie(models.Model):
    nume = models.CharField(primary_key=True,max_length=50, unique=True)
    descriere = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='data_base_images/categorii', null=True, blank=True)
    def __str__(self):
        return self.nume
    
class Furnizor(models.Model):
    id_furnizor = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nume = models.CharField(max_length=100, validators=[validare_nume])
    biografie = models.TextField(null=True)
    telefon = models.CharField(max_length=15, validators=[validate_telefon])
    email = models.EmailField(validators=[validate_email])
    poza = models.ImageField(upload_to='data_base_images/furnizori', null=True, blank=True)
    def __str__(self):
        return self.nume
    
class Oferta(models.Model):
    id_jucarie = models.ForeignKey(Jucarie, on_delete=models.CASCADE)
    procent_reducere = models.DecimalField(max_digits=4, decimal_places=2,
        default=10,
        validators=[
            MinValueValidator(1, message="Reducerea trebuie sa fie de cel putin 1%."),
            MaxValueValidator(90, message="Reducerea nu poate fi mai mare de 90%.")
        ])
    data_inceput = models.DateField()
    data_sfarsit = models.DateField()
    activa = models.BooleanField(default=True)
    def clean(self):
        super().clean() 
        if self.data_sfarsit < self.data_inceput:
            raise ValidationError(
                {'data_sfarsit': "Data de sfarsit nu poate fi inaintea datei de inceput."}
            )
    def __str__(self):
        return f"Oferta pentru {self.id_jucarie.nume}: {self.procent_reducere}% reducere"
class EvenimentPromotional(models.Model):
    nume = models.CharField(max_length=100)
    detalii = models.TextField(blank=True, null=True)
    id_jucarie = models.ManyToManyField(Jucarie)
    data_inceput = models.DateField()
    data_sfarsit = models.DateField()
    def clean(self):
        super().clean() 
        if self.data_sfarsit < self.data_inceput:
            raise ValidationError(
                {'data_sfarsit': "Data de sfarsit nu poate fi inaintea datei de inceput."}
            )
    def __str__(self):
        return self.nume