import datetime
import locale
def functie_de_data():
    locale.setlocale(locale.LC_TIME, 'Romanian')
    acum = datetime.datetime.now()
    data_formatata = acum.strftime('%A, %d %B %Y').capitalize()
    ora_formatata = acum.strftime('%H:%M:%S')
    data=[(data_formatata),(ora_formatata)]
    return data

def get_ip(request):
    str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if str_lista_ip:
        return str_lista_ip.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR')