import datetime
import os
import json
from random import random, sample
import secrets
import string
from django.core.mail import send_mail
import time
from django.shortcuts import get_object_or_404, render,redirect
from .middleware import LogMiddleware
from .models import Jucarie, Categorie, UtilizatorPersonalizat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import AdaugaJucarieForm, ProduseFilterForm, ContactForm, InregistrareForm, FormInregistrareZi
from .utilFunctions import get_ip,functie_de_data
from django.contrib.auth import login, logout
def capitalize_sentences(text):
    result = ""
    capitalize_next = True 
    
    for i in range(len(text)):
        char = text[i]
        if capitalize_next and char.isalpha():
            result += char.upper()
            capitalize_next = False
        else:
            result += char
           
            if char in ".!?":
                capitalize_next = True
                
    return result

def tabel_procesare(tabel):
    tabel=tabel.split(',')
    definitor=[]
    if 'tot' in tabel:
        tabel=['id','ip','url','data']
    for col in tabel:
        if col=='id':
            definitor.append(0)
        elif col =='ip':
            definitor.append(1)
        elif col == 'url':
            definitor.append(2)
        elif col == 'data':
            definitor.append(3)
    return definitor,tabel
def afisare_parametri(log_list,nr_accesari):
    parametrii = log_list[-1].lista_parametrii() if nr_accesari>0 else []
    nr_parametrii = len(parametrii)
    response_content =[nr_parametrii]
    for p in parametrii:
        response_content.append(p)
    return response_content

    
def parsare_ids(id_uri,duplicate):
    id_uri = list(','.join(id_uri).split(',')) if id_uri else None
    id_uri=list(map(int,id_uri))
    if id_uri and (duplicate is False or duplicate == "False"):
        id_uri = [id_uri[i] for i in range(len(id_uri)) if id_uri[i] not in id_uri[:i]]
    return id_uri
def lowest_most_visited(log_list):
    dict_accesari = {}
    for accesare in log_list:
        url=accesare.url.strip('/')
        if url in dict_accesari:
            dict_accesari[url]+=1
        else:
            dict_accesari[url]=1
    mn=float('inf')
    mx=float('-inf')
    for url in dict_accesari:
        if dict_accesari[url]<mn:
            mn=dict_accesari[url]
        if dict_accesari[url]>mx:
            mx=dict_accesari[url]
    cele_mai_putin_accesate = [url for url in dict_accesari if dict_accesari[url]==mn]
    cele_mai_multe_accesari = [url for url in dict_accesari if dict_accesari[url]==mx]
    return cele_mai_putin_accesate, cele_mai_multe_accesari

def filtrare(parametru,obPagina):
    
    if parametru == 'a':
        lista_sortata = sorted(obPagina.object_list, key=lambda jucarie: jucarie.pret)
        return lista_sortata
    if parametru == 'd':
        lista_sortata = sorted(obPagina.object_list, key=lambda jucarie: jucarie.pret, reverse=True)
        return lista_sortata
    return obPagina.object_list
# Create your views here.
from django.http import HttpResponse
def index(request):
    toate_produsele = list(Jucarie.objects.filter(stoc__gt=0).select_related('nume_categorie'))
    nr_produse = min(6, len(toate_produsele))
    produse_random = sample(toate_produsele, nr_produse) if toate_produsele else []
    categorii = Categorie.objects.all()[:4]
    return render(request, 'aplicatie_exemplu/paginaPrincipala.html', {
        'produse_recomandate': produse_random,
        'categorii_afisate': categorii,
    })
def in_lucru(request):
    return render(request, 'aplicatie_exemplu/in_lucru.html')
def despre(request):
    return render(request, 'aplicatie_exemplu/despre.html')

def contact(request):
   
    form = ContactForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            mesaj = data['mesaj']
            data_nasterii = data['data_nasterii']
            tip = data['tip_mesaj']
            zile = data['minim_zile_asteptare']
            
            today = datetime.date.today()
            ani = today.year - data_nasterii.year
            luni = today.month - data_nasterii.month
            if today.day < data_nasterii.day:
                luni -= 1
            if luni < 0:
                ani -= 1
                luni += 12
            varsta_formatata = f"{ani} ani și {luni} luni"
            toSpl=string.punctuation
            for p in toSpl:
                mesaj = mesaj.replace(p, ' ')
            mesaj = mesaj.replace('\n', ' ')
            mesaj = " ".join(mesaj.split())
            mesaj = capitalize_sentences(mesaj)
            
            urgent = False
            if (tip in ['review', 'cerere'] and zile == 2) or (tip in ['intrebare','reclamatie','programare'] and zile == 4):
                urgent = True
            data['urgent'] = urgent
            timestamp = int(time.time())
            nume_fisier = f"mesaj_{timestamp}[{'urgent_' if urgent else ''}]    {data['nume']}.txt"
            date_de_salvat = data.copy()
            date_de_salvat.pop('confirm_email', None)
            date_de_salvat.update({
                'mesaj': mesaj,
                'varsta': varsta_formatata,
                'urgent': urgent,
                'ip': get_ip(request),
                'data_trimiterii': functie_de_data(),
            })
            date_de_salvat['data_nasterii'] = str(data['data_nasterii'])
            cale_folder = os.path.join(os.path.dirname(__file__), 'Mesaje')
            if not os.path.exists(cale_folder):
                os.makedirs(cale_folder)
            cale_completa = os.path.join(cale_folder, nume_fisier)
            with open(cale_completa, 'w', encoding='utf-8') as fisier_json:
                json.dump(date_de_salvat, fisier_json, indent=4, ensure_ascii=False)
            
            return render(request, 'aplicatie_exemplu/paginaPrincipala.html', {
                'nume': form.cleaned_data['nume'],
                'prenume': form.cleaned_data['prenume']
            })

    else:
        form = ContactForm()
    return render(request, 'aplicatie_exemplu/contact.html', {'form': form})

def adauga_produs(request):
    form= AdaugaJucarieForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            jucarie_noua = form.save(commit=False)
            cost_crosetare = form.cleaned_data['pret_achizitie']
            adaos = form.cleaned_data['procent_adaugare']
            jucarie_noua.pret = cost_crosetare + (cost_crosetare * adaos)
            jucarie_noua.save()
            return render(request,'aplicatie_exemplu/adauga_jucarie.html', {'form': AdaugaJucarieForm()})
    else:
        form = AdaugaJucarieForm()
    return render(request,'aplicatie_exemplu/adauga_jucarie.html',{'form': form})
    
    
def log(request):
    
    ultimele = request.GET.get('ultimele',None)
    accesari = request.GET.get('accesari',None)
    id_uri = request.GET.getlist('iduri')
    duplicate = request.GET.get('duplicate',False)
    tabel = request.GET.get('tabel',None)
    log_list = LogMiddleware.get_log_list()
    nr_accesari = LogMiddleware.nr_accesari()
    putin_accesate, mult_accesate = lowest_most_visited(log_list)
    informatie_totala={}  
    informatie_totala['numar_parametrii'] = afisare_parametri(log_list,nr_accesari)
    informatie_totala['numar_accesari'] = nr_accesari
    informatie_totala['detalii_accesari'] = []
    informatie_totala['erori'] = []
    
    if id_uri != [] and id_uri!=['']:
        try:
            id_uri = parsare_ids(id_uri,duplicate)
            
            for i in id_uri:
                if i>0 and i<=nr_accesari:
                    informatie_totala['detalii_accesari'].append(log_list[i-1])
        except:
            informatie_totala['erori'].append("Eroare in Id, specificati din nou")
    else:
        if ultimele is None or ultimele == '':
            for i in log_list:
                informatie_totala['detalii_accesari'].append(i)
    
        else:
            if not ultimele.isdigit() or float(ultimele)!=int(ultimele) or int(ultimele)<=0:
                informatie_totala['erori'].append("Ultimele trebuie sa fie un numar intreg pozitiv")
            else:
                error_message=False
                remember=int
                ultimele=int(ultimele)
                if ultimele>nr_accesari:
                    error_message=True
                    remember = ultimele
                    ultimele = nr_accesari
                
                for i in range(nr_accesari-1,nr_accesari-ultimele-1,-1):
                    informatie_totala['detalii_accesari'].append(log_list[i])
                if error_message:
                    informatie_totala['erori'].append(f"Exista doar {nr_accesari} accesari fata de {remember} accesari cerute")

    if tabel is not None and  tabel !='':        
        definitor,tabel = tabel_procesare(tabel)
        context = {'antete' : tabel, 'randuri': informatie_totala['detalii_accesari'],'definire':definitor,
                   'putin_accesate':putin_accesate,'mult_accesate':mult_accesate,'erori':informatie_totala['erori']}
        return render(request,'aplicatie_exemplu/tabelLog.html',context)
    else:
        context = {'detalii_accesari': informatie_totala['detalii_accesari'],
                   'putin_accesate':putin_accesate,'mult_accesate':mult_accesate,'numar_accesari':accesari,'numar_parametrii':informatie_totala['numar_parametrii'],'erori':informatie_totala['erori']}
        return render(request, 'aplicatie_exemplu/paginaLog.html',context)



def afiare_produse(request):
    
    form = ProduseFilterForm(request.GET)
    date= form.cleaned_data if form.is_valid() else {}
    mesaj_eroare = None
    mesaj_paginare=None
    elem_pe_pagina = 4
    categorie = request.GET.get('categorie',None)
    sortare = date.get('pret_sortare')
    
    if categorie:
        lista_jucarii = Jucarie.objects.filter(nume_categorie=categorie)
    else:
        lista_jucarii = Jucarie.objects.all()
        
    if date.get('nume'):
            lista_jucarii = lista_jucarii.filter(nume__icontains=date['nume'])
    if date.get('nume_categorie'):
            lista_jucarii = lista_jucarii.filter(nume_categorie=date['nume_categorie'])        
    if date.get('marime'):
            lista_jucarii   = lista_jucarii.filter(marime=date['marime'])
    if date.get('stoc'):
            lista_jucarii = lista_jucarii.filter(stoc__gt=0)
    if date.get('pret_min') is not None:
            lista_jucarii = lista_jucarii.filter(pret__gte=date['pret_min'])
    if date.get('pret_max') is not None:
            lista_jucarii = lista_jucarii.filter(pret__lte=date['pret_max'])
   

    
    if date.get('paginare'):
        elem_pe_pagina = date['paginare']
    if elem_pe_pagina > len(lista_jucarii):
        mesaj_paginare = f"Exista doar {len(lista_jucarii)} produse care corespund criteriilor de filtrare, deci nu se poate afisa {elem_pe_pagina} produse pe pagina."
        elem_pe_pagina = len(lista_jucarii) 
    if len(lista_jucarii)==0:
        return render(request,'aplicatie_exemplu/produs.html',{
            'form':form,
            'mesaj_eroare':"Nu s-au gasit produse care sa corespunda criteriilor de filtrare",
        })
    paginator = Paginator(lista_jucarii,elem_pe_pagina)
    
    nrPagina = request.GET.get('pagina')
    try:
        obPagina = paginator.page(nrPagina)
    except PageNotAnInteger:
        obPagina=paginator.page(1)
    except EmptyPage:
        obPagina =paginator.page(paginator.num_pages)
    
    obPagina.object_list = filtrare(sortare,obPagina)
    if(len(lista_jucarii)==0):
        mesaj_eroare="Nu s-au gasit produse care sa corespunda criteriilor de filtrare"
    return render(request,'aplicatie_exemplu/produs.html',{
        'form':form,
        'pagina':obPagina,
        'mesaj_eroare':mesaj_eroare,
    })

def detalii_produs(request,id_produs):
    prod = get_object_or_404(Jucarie, id=id_produs)

    return render(request, 'aplicatie_exemplu/detalii_produs.html',{
        'produs':prod,
    })
    
    
def inregistrare_utilizator(request):
    if request.method == 'POST':
        form = InregistrareForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            cod_random = secrets.token_urlsafe(16)
            user.cod = cod_random 
            user.save()
            link_confirmare = f"http://127.0.0.1:8000/email_confirmare/{cod_random}/"
            send_mail(
                subject='Confirmare înregistrare',
                message=f'Bun venit, {user.first_name}! Pentru a-ti confirma inregistrarea, te rugam sa accesezi urmatorul link: {link_confirmare}',
                from_email='admin@exemplu.ro',
                recipient_list=[user.email],
                )
            
            return redirect('login')
    else:
        form = InregistrareForm()
    
    return render(request, 'aplicatie_exemplu/inregistrare.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = FormInregistrareZi(request, data=request.POST)
        if form.is_valid():   
            user = form.get_user()
            actual_rn = request.user
            if actual_rn.email_confirmat == False:
                return HttpResponse("Ne pare rau, nu ti-ai confirmat emailul")
          
            login(request, user)
            if form.cleaned_data.get('remember_me'):
                request.session.set_expiry(86400)
            else:
                request.session.set_expiry(0)
            return redirect('profil')
    else:
        form = FormInregistrareZi()
    return render(request, 'aplicatie_exemplu/login.html', {'form': form})

def profil_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    info = request.session.get('date_utilizator')
    if not info:
        user = request.user
        info = {
            'username': user.username,
            'email': user.email,
            'nume_complet': f"{user.first_name} {user.last_name}",
            'telefon': getattr(user, 'telefon', 'Nespecificat'),
            'oras': getattr(user, 'oras', 'Nespecificat'),
            'tara': getattr(user, 'tara', 'Nespecificat'),
            'data_nasterii': str(getattr(user, 'data_nasterii', 'Nespecificat')),
        }
        request.session['date_utilizator'] = info
        request.session.modified = True 

    return render(request, 'aplicatie_exemplu/profil.html', {'info': info})

def email_confirmare(request, cod):
    users = UtilizatorPersonalizat.objects.filter(cod=cod)
    print(f"--- DEBUG: Codul primit din URL este: {cod} ---")
    toti_userii = UtilizatorPersonalizat.objects.all()
    for u in toti_userii:
        print(f"User: {u.username} | Cod în DB: {u.cod}")
        
    if users.exists():
        user = users.first()
        user.email_confirmat = True
        user.save()
        return render(request, 'aplicatie_exemplu/email_confirmare.html', {'prenume': user.first_name, 'nume': user.last_name})
    else:
        return HttpResponse("Cod de confirmare invalid.")

def cart_view(request):
    """View for displaying the shopping cart page"""
    return render(request, 'aplicatie_exemplu/cart.html')


from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def trimite_comanda(request):
    try:
        data = json.loads(request.body)
        instagram = data.get('instagram', '').strip()
        locatie = data.get('locatie', '').strip()
        cart = data.get('cart', [])
        
        if not instagram or not locatie:
            return JsonResponse({'success': False, 'error': 'Numele de Instagram și locația sunt obligatorii.'}, status=400)
        
        if not cart or not isinstance(cart, list):
            return JsonResponse({'success': False, 'error': 'Coșul de cumpărături este gol.'}, status=400)
        
        # Build email body
        email_subject = f"Comandă Nouă Amigurumi - @{instagram}"
        
        email_body = f"A fost înregistrată o nouă comandă pe site-ul Amigurumi World!\n\n"
        email_body += f"Detalii Client:\n"
        email_body += f"----------------------------------------\n"
        email_body += f"Nume cont Instagram: @{instagram}\n"
        email_body += f"Locație / Adresă: {locatie}\n"
        email_body += f"Data: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\n"
        
        email_body += f"Produse Comandate:\n"
        email_body += f"----------------------------------------\n"
        
        subtotal = 0
        for index, item in enumerate(cart, 1):
            item_nume = item.get('nume', 'Produs necunoscut')
            item_pret = float(item.get('pret', 0))
            item_cantitate = int(item.get('quantity', 1))
            item_subtotal = item_pret * item_cantitate
            subtotal += item_subtotal
            
            email_body += f"{index}. {item_nume}\n"
            email_body += f"   Cantitate: {item_cantitate} x {item_pret:.2f} RON\n"
            email_body += f"   Subtotal: {item_subtotal:.2f} RON\n\n"
            
        livrare_gratuita = subtotal >= 200
        cost_livrare = 0 if livrare_gratuita else 15
        total_final = subtotal + cost_livrare
        
        email_body += f"----------------------------------------\n"
        email_body += f"Subtotal produse: {subtotal:.2f} RON\n"
        email_body += f"Cost livrare: {'GRATUITĂ' if livrare_gratuita else f'{cost_livrare:.2f} RON'}\n"
        email_body += f"TOTAL DE PLATĂ: {total_final:.2f} RON\n"
        email_body += f"----------------------------------------\n\n"
        email_body += f"Contactați clientul pe Instagram pentru confirmare și detalii de plată."
        
        send_mail(
            subject=email_subject,
            message=email_body,
            from_email='webmaster@localhost',
            recipient_list=['fanelmunteanu568@gmail.com'],
            fail_silently=False,
        )
        
        return JsonResponse({'success': True, 'message': 'Comanda a fost trimisă cu succes!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Eroare la procesarea comenzii: {str(e)}'}, status=500)

    