from .utils import Accesare
from .utilFunctions import  get_ip


class LogMiddleware:
    log_list = []
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        acc = Accesare(get_ip(request),request.path, request.GET)
        LogMiddleware.log_list.append(acc)
        response = self.get_response(request)
        return response
    @staticmethod
    def get_log_list():
        return LogMiddleware.log_list
    @staticmethod
    def nr_accesari():
        return len(LogMiddleware.log_list)
    
                