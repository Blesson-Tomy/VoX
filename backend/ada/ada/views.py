from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import views

def home(request):
    return render(request, 'home.html')