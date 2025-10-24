from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("<center><h1>BlackGate en implementación 🚀</h1></center>")

