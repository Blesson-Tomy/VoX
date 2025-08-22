from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django import forms
from .models import CaseIntake
from . import views

class CaseIntakeForm(forms.ModelForm):
    class Meta:
        model = CaseIntake
        fields = ['case_type', 'complainant_name', 'contact_number', 
                 'email', 'description', 'supporting_documents']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

def home(request):
    return render(request, 'home.html')

def case_intake(request):
    if request.method == 'POST':
        form = CaseIntakeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Case submitted successfully!')
            return redirect('case_intake')
    else:
        form = CaseIntakeForm()
    return render(request, 'ada/case_intake.html', {'form': form})