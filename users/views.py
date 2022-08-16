import os
from django.views import View
from django.views.generic import FormView
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from . import forms

# Create your views here.
class LoginView(FormView):
    
    template_name= "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")
    
    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
            
        if user is not None:
            login(self.request, user)
            
        return super().form_valid(form)
    
    ''' def get(self, request):
        form = forms.LoginForm(initial={
            "email": "abcd@example.com"
        })
        return render(request, "users/login.html", {
            "form": form
        })
    
    def post(self, request):
        form = forms.LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request,user)
                return redirect(reverse("core:home"))
            
        return render(request, "users/login.html", {
            "form": form
        }) '''
        
def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))

class SignUpView(FormView):
    
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    initial = {
        "first_name": "abcd",
        "last_name": "efgh",
        "email": "abcd@example.com"
    }
    
    def form_valid(self, form):
        form.save()
        
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
            
        if user is not None:
            login(self.request, user)
            
        return super().form_valid(form)
    
def github_login(request):
    client_id = os.envrion.get("GH_ID")
    redirect_uri = "https://127.0.0.1:8000/users/login/github/callback"
    return redirect(f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user")

def github_callback(request):
    
    pass