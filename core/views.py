# core, views.py:

from django.shortcuts import render
from django.http import HttpResponse

# note: cbvs are in app tasks and users
def home(request):
    return render(request, 'home.html')  # redirect ?
    # return HttpResponse("<h1>This is core Home</h1>")
    

def no_permission(request):
    return render(request, 'no_permission.html')

