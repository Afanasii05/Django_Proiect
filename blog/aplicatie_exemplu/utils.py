from urllib.parse import urlparse
from .utilFunctions import functie_de_data
class Accesare:
    id_counter = 1
    def __init__(self,ip,url,parametrii):
        self.id = Accesare.id_counter
        self.ip_client = ip
        self.url = url  
        self.data = functie_de_data()
        self.parametrii = parametrii
        Accesare.id_counter += 1
    def __str__(self):
        return f"ID: {self.id}, IP: {self.ip_client}, URL: {self.url}, Data: {self.data}"
    
    def show_non_detalii(self):
        return f"ID: {self.id}, IP: {self.ip_client}, URL: {self.url}"
    def lista_parametrii(self):
        return self.parametrii 
    def url_full(self):
        return self.url
    def data_formatata(self,format=''):
        if format == '':
            return self.data
        elif format == "zi":
            return self.data[0]
        else:
            return self.data[1]
    