# core, views.py:

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'home.html')  # redirect ?
    # return HttpResponse("<h1>This is core Home</h1>")
    

def no_permission(request):
    return render(request, 'no_permission.html')

