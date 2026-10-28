from django.http import HttpResponse

def hello(request):
    return HttpResponse("Welcome to PesaWay Payment Simulator")