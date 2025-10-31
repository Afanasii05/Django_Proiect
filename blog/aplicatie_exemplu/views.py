from django.shortcuts import render
from .middleware import LogMiddleware

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
# Create your views here.
from django.http import HttpResponse
def info(request):
    return render(request, 'aplicatie_exemplu/info.html')

def index(request):
    return render(request, 'aplicatie_exemplu/paginaPrincipala.html')
def in_lucru(request):
    return render(request, 'aplicatie_exemplu/in_lucru.html')
def despre(request):
    return render(request, 'aplicatie_exemplu/despre.html')



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
        print(informatie_totala['detalii_accesari'])
        context = {'detalii_accesari': informatie_totala['detalii_accesari'],
                   'putin_accesate':putin_accesate,'mult_accesate':mult_accesate,'numar_accesari':accesari,'numar_parametrii':informatie_totala['numar_parametrii'],'erori':informatie_totala['erori']}
        return render(request, 'aplicatie_exemplu/paginaLog.html',context)

