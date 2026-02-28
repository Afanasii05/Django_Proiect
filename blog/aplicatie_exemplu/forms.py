import re
import string
from django import forms
from .models import Jucarie, Categorie, UtilizatorPersonalizat
from django.core.exceptions import ValidationError
from .utilFunctions import functie_de_data
import re
import datetime
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


def verifica_format_text(text): 
    pattern = r'^[A-Z][A-Za-z\s-]*$'
    if not re.match(pattern, text):
        return False
    return True
def verificare_Litera_Mare(text):
    if len(text.split()) < 2:
        return True
    second = text.split()[1] if len(text.split()) > 1 else ''
    if second[0].isupper():
        return True
    return False
class ProduseFilterForm(forms.Form):
    nume = forms.CharField(
    required=False, 
    label='Nume Jucarie',
    widget=forms.TextInput(attrs={'placeholder': 'Caută după nume...', 'class': 'form-control'})
)
    pret_sortare = forms.ChoiceField(required=False, choices=[('', 'Nicio sortare'), ('a', 'Pret crescator'), ('d', 'Pret descrescator')],
    									widget=forms.Select(attrs={'class': 'form-control'}))
    nume_categorie = forms.ModelChoiceField(queryset=Categorie.objects.all(), required=False, label='Categorie',
    										widget=forms.Select(attrs={'class': 'form-control'}))
    marime = forms.ChoiceField(
        required=False, 
        label='Marime',
        choices=[('', 'Toate marimile')] + Jucarie.marimeChoices.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    pret_min = forms.DecimalField(required=False,initial=0, label='Pret minim', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pret minim'}))
    pret_max = forms.DecimalField(required=False,initial=1000, label='Pret maxim', min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pret maxim'}))
    stoc = forms.BooleanField(required=False, label='Doar produse in stoc',
    							widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    paginare = forms.IntegerField(required=False,min_value=1, label='Produse pe pagina', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Produse pe pagina'}))
    def clean_paginare(self):
        paginare = self.cleaned_data.get('paginare')
        if paginare is not None and paginare <= 0:
            raise ValidationError("Numarul de produse pe pagina trebuie sa fie un numar pozitiv.")
        return paginare
    def clean_pret_min(self):
        pret_min = self.cleaned_data.get('pret_min')
        if pret_min is not None and pret_min < 0:
            raise ValidationError("Pretul minim trebuie sa fie un numar pozitiv.")
        return pret_min
    def clean_nume(self):
        nume = self.cleaned_data.get('nume')
        if nume and len(nume) < 5:
            raise ValidationError("Numele jucariei trebuie sa aiba cel putin 5 caractere.")
        return nume
    def clean(self):
        cleaned_data = super().clean()
        pret_min = cleaned_data.get('pret_min')
        pret_max = cleaned_data.get('pret_max')
        if pret_min is not None and pret_max is not None and pret_min > pret_max:
            self.add_error('pret_min', 'Pretul minim nu poate fi mai mare decat pretul maxim.')
        return cleaned_data
        
class ContactForm(forms.Form):
    nume = forms.CharField(required=True,max_length=100, label='Nume', widget=forms.TextInput(attrs={'class': 'form-control'}))
    prenume = forms.CharField(required=False,max_length=100, label='Prenume', widget=forms.TextInput(attrs={'class': 'form-control'}))
    CNP = forms.CharField(required=False,min_length=13, 
        max_length=13, label='CNP', widget=forms.TextInput(attrs={'class': 'form-control'}))
    data_nasterii = forms.DateField(
        required=True, 
        label='Data nașterii', 
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    email = forms.EmailField(required=True,label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    confirm_email = forms.EmailField(required=True,label='Confirmare Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    tip_mesaj = forms.ChoiceField(required=True,initial='neselectat', label='Tip mesaj', choices=[('neselectat','Neselectat'),('intrebare', 'Intrebare'), ('cerere', 'Cerere'), ('review', 'Review'),('reclamatie','Reclamatie'),('programare','Programare')], widget=forms.Select(attrs={'class': 'form-control'}))
    subiect = forms.CharField(required=True,label='Subiect', widget=forms.TextInput(attrs={'class': 'form-control'}))
    minim_zile_asteptare = forms.IntegerField(required=True,min_value=0,label="Pentru review-uri/cereri minimul de zile de asteptare trebuie setat de la 4 incolo iar pentru cereri/intrebari de la 2 incolo. Maximul e 30.", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    mesaj = forms.CharField(required=True,label='Mesaj + semnatura', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    def clean_CNP(self):
        CNP = self.cleaned_data.get('CNP')
        if CNP and (not CNP.isdigit() or len(CNP) != 13):
            raise ValidationError("CNP-ul trebuie sa contina exact 13 cifre.")
        if CNP[0] not in '1256':
            raise ValidationError("CNP-ul trebuie sa inceapa cu cifra 1 sau 2.")
        an=CNP[1:3]
        luna=CNP[3:5]
        zi=CNP[5:7]
        if(CNP[0] in '12'):
            an='19'+an
        elif(CNP[0] in '56'):
            an='20'+an
        d_luni_zile = {'01': 31, '02': 29, '03': 31, '04': 30, '05': 31, '06': 30, '07': 31, '08': 31, '09': 30, '10': 31, '11': 30, '12': 31}
        if(int(an)>int(functie_de_data()[0][-4:])):
            raise ValidationError("CNP-ul nu poate indica o data de nastere in viitor.")
        if(int(luna)<1 or int(luna)>12):
            raise ValidationError("CNP-ul trebuie sa contina o luna valida.")
        if(int(zi)<1 or int(zi)>d_luni_zile.get(luna, 0)):
            raise ValidationError("CNP-ul trebuie sa contina o zi valida.")
        return CNP
    def clean_tip_mesaj(self):
        tip_mesaj = self.cleaned_data.get('tip_mesaj')
        if tip_mesaj == 'neselectat':
            raise ValidationError("Trebuie selectat un tip de mesaj.")
        return tip_mesaj
    def clean_mesaj(self):
        mesaj = self.cleaned_data.get('mesaj')
        toSplit = string.punctuation
        for p in toSplit:
            mesaj = mesaj.replace(p, ' ')
        ls_cuv = mesaj.split()
        if len(ls_cuv)<5:
            raise ValidationError("Mesajul trebuie sa contina cel putin 5 cuvinte.")
        if len(ls_cuv)>100:
            raise ValidationError("Mesajul nu poate contine mai mult de 100 de cuvinte.")
        for cuv in ls_cuv:
            if(len(cuv)>15):
                raise ValidationError("Niciun cuvant din mesaj nu poate depasi 15 caractere.")
            if cuv in "http://" or cuv in "https://":
                raise ValidationError("Mesajul nu poate contine link-uri.")
        return mesaj
    def clean_data_nasterii(self):
        data_nasterii = self.cleaned_data.get('data_nasterii')
        if data_nasterii:
       
            today = datetime.date.today()
        varsta = today.year - data_nasterii.year - ((today.month, today.day) < (data_nasterii.month, data_nasterii.day))
        if varsta < 18:
            raise ValidationError(f"Trebuie să aveți cel puțin 18 ani. Vârsta detectată: {varsta} ani.")
        return data_nasterii
   
    def clean_nume(self):
        nume = self.cleaned_data.get('nume')
        if not verifica_format_text(nume):
            raise ValidationError("Numele trebuie sa inceapa cu majuscula si sa contina doar litere, spatii sau cratime.")
        if not verificare_Litera_Mare(nume):
            raise ValidationError("Al doilea cuvant din nume  trebuie sa inceapa cu majuscula.") 
        return nume
    def clean_prenume(self):
        prenume = self.cleaned_data.get('prenume')
        if prenume and not verifica_format_text(prenume):
            raise ValidationError("Prenumele trebuie sa inceapa cu majuscula si sa contina doar litere, spatii sau cratime.")
        if prenume and not verificare_Litera_Mare(prenume):
            raise ValidationError("Al doilea cuvant din prenume trebuie sa inceapa cu majuscula.")
        return prenume
    def clean_subiect(self):
        subiect = self.cleaned_data.get('subiect')
        if not verifica_format_text(subiect):
            raise ValidationError("Subiectul trebuie sa inceapa cu majuscula si sa contina doar litere, spatii sau cratime.")
        return subiect
    def clean(self):
        di_tip_zile = {'intrebare': 4, 'cerere': 2, 'review': 2, 'reclamatie': 4, 'programare': 4}
        email = self.cleaned_data.get('email')
        confirm_email = self.cleaned_data.get('confirm_email')
        if email != confirm_email:
            self.add_error ("confirm_email", "Adresele de email nu corespund.")
        domeniu = email.split('@')[-1].lower()
        if domeniu in ['guerillamail.com', 'yopmail.com']:
            self.add_error ("email", "Adrese temporare nu sunt acceptate.")
            
        cleaned_data = super().clean()
        nr_zile_asteptare = cleaned_data.get('minim_zile_asteptare')
        tip_mesaj = cleaned_data.get('tip_mesaj')
        if di_tip_zile.get(tip_mesaj) > nr_zile_asteptare or nr_zile_asteptare > 30:
                self.add_error('minim_zile_asteptare', f"Pentru tipul de mesaj selectat, numarul minim de zile de asteptare trebuie sa fie intre {di_tip_zile[tip_mesaj]} si 30.")
        mesaj=cleaned_data.get('mesaj')
        nume=cleaned_data.get('nume')
        toSpl = string.punctuation
        for p in toSpl:
            mesaj = mesaj.replace(p, ' ')   
        if mesaj and (mesaj.split()[-1].lower() not in nume.lower().split()):
            self.add_error('mesaj', "Mesajul trebuie sa se incheie cu numele de familie pentru a servi drept semnatura.")
        return cleaned_data


class AdaugaJucarieForm(forms.ModelForm):
    pret_achizitie = forms.DecimalField(required=True, label='Pret total de crosetare', help_text="Pretul de fabricare total", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    procent_adaugare = forms.DecimalField(required=True, label='Procent adaos comercial', help_text="Procentul de adaos comercial aplicat la pretul de crosetare pentru a obtine pretul final", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Jucarie
        fields = ['nume','descriere', 'stoc', 'marime', 'nume_categorie', 'poza']
        labels = {
            'nume': 'Denumire Jucărie',
            'stoc': 'Unități disponibile'
        }
    def clean_nume(self):
        nume= self.cleaned_data.get('nume')
        if verificare_Litera_Mare(nume) == False:
            raise ValidationError("Al doilea cuvant din nume  trebuie sa inceapa cu majuscula.")
        if verifica_format_text(nume) == False:
            raise ValidationError("Numele trebuie sa inceapa cu majuscula si sa contina doar litere, spatii sau cratime.")
        if len(nume)<2:
            raise ValidationError("Numele jucariei trebuie sa aiba cel putin 2 caractere.")
        return nume
    def clean_stoc(self):
        stoc = self.cleaned_data.get('stoc')
        if stoc is not None and stoc < 0:
            raise ValidationError("Stocul nu poate fi negativ.")
        return stoc
    def clean_nume_categorie(self):
        nume_categorie = self.cleaned_data.get('nume_categorie')
        if nume_categorie is None:
            raise ValidationError("Categoria este obligatorie.")
        if verificare_Litera_Mare(nume_categorie.nume) == False:
            raise ValidationError("Al doilea cuvant din nume categorie trebuie sa inceapa cu majuscula.")
        return nume_categorie
    def clean(self):
        cleaned_data = super().clean()
        pret_achizitie = cleaned_data.get('pret_achizitie')
        procent_adaugare = cleaned_data.get('procent_adaugare')
        if pret_achizitie + (pret_achizitie * procent_adaugare) < pret_achizitie:
            self.add_error('procent_adaugare', "Nu obtineti profit, reintroduceti procentul de adaos comercial.")
        return cleaned_data
        

class InregistrareForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Adresa de email este obligatorie.")
    class Meta(UserCreationForm.Meta):
        model = UtilizatorPersonalizat
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'email', 
            'telefon', 'tara', 'oras', 'data_nasterii', 'prenume'
        )

    def clean_telefon(self):
        tel = self.cleaned_data.get('telefon')
        if tel:
            if not tel.isdigit():
                raise ValidationError("Numarul de telefon trebuie sa contina doar cifre.")
            if len(tel) < 10:
                raise ValidationError("Numarul de telefon trebuie sa aiba cel putin 10 cifre.")
        return tel

    def clean_oras(self):
        oras = self.cleaned_data.get('oras')
        if oras and any(char.isdigit() for char in oras):
            raise ValidationError("Numele orasului nu poate contine cifre.")
        return oras

    def clean_data_nasterii(self):
        data_n = self.cleaned_data.get('data_nasterii')
        if data_n and data_n > datetime.date.today():
            raise ValidationError("Data nașterii nu poate fi în viitor.")
        return data_n
    
class FormInregistrareZi(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label="Ține-mă logat o zi")