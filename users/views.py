import os
import requests
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView, DetailView, UpdateView
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import forms, models, mixins


# Create your views here.
class LoginView(mixins.LoggedOutOnlyView, FormView):
    
    template_name= 'users/login.html'
    form_class = forms.LoginForm
    #success_url = reverse_lazy("core:home")
    
    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
            
        if user is not None:
            login(self.request, user)
            
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")

        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")
    
def log_out(request):
    logout(request)
    messages.info(request, f"See you later")
    return redirect(reverse("core:home"))

class SignUpView(mixins.LoggedOutOnlyView, FormView):
    
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    
    def form_valid(self, form):
        form.save()
        
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
            
        if user is not None:
            login(self.request, user)
            
        return super().form_valid(form)
    
def github_login(request):
    client_id = os.environ.get("GH_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user")

class GithubException(Exception):
    pass

def github_callback(request):
    
    try:
        code = request.GET.get("code", None)
        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        
        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"}
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            
            if error is not None: # when error occurs
                raise GithubException("Something went wrong!")
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get("https://api.github.com/user", headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json"
                    }
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                
                if username is not None: # when user already exists
                    name = profile_json.get('name')
                    email = profile_json.get('email')
                    bio = profile_json.get('bio')
                    
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(f"Please log in with: {user.login_method}")
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email, first_name=name, username=email, bio=bio,
                            login_method=models.User.LOGIN_GITHUB
                        )
                        user.set_unusable_password()
                        user.save()
                    
                    login(request, user)
                    messages.success(request, f"Welcome back {user.first_name} !")
                    return redirect(reverse("core:home"))
                
                else:
                    raise GithubException("Can't get your profile")
        else:
            raise GithubException("Can't get code")
    except GithubException as e: # when exception occures, go to login page
        # send error message
        messages.error(request, e)
        return redirect(reverse("users:login"))
    
def kakao_login(request):
    app_key = os.environ.get("KAKAO_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_key}&redirect_uri={redirect_uri}"
    )
    
class KakaoException(Exception):
    pass
    
def kakao_callback(request):
    try:
        code = request.GET.get("code")
        client_id = request.GET.get("KAKAO_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        
        if error is not None:
            raise KakaoException("Can't get authorization code.")
        
        access_token = token_json.get("access_token")
        profile_request = requests.get("https://kapi.kakao.com/v2/user/me", headers={
            "Authorization": f"Bearer {access_token}"
        })
        profile_json = profile_request.json()
        email = profile_json.get("kaccount_email", None)
        
        if email is None:
            raise KakaoException("Please also give me your email")
        
        properties = profile_json.get("properties")
        nickname = properties.get("nickname")
        profile_image = properties.get("profile_image")
        
        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException(f"Please log in with: {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO
            )
            user.set_unusable_password()
            user.save()
            
            if profile_image is not None:
                photo_request = requests.get(profile_image)
                user.avatar.save(
                    f"{nickname}-avatar", ContentFile(photo_request.content)
                )
                
        login(request, user)
        messages.success(request, f"Welcome back {user.first_name}!")
        return redirect(reverse("core:home"))
            
    except KakaoException as e:
        messages.error(request, e)
        raise redirect(reverse("users:login"))

class UserProfileView(DetailView):
    
    model = models.User
    context_object_name = "user_obj"

    """ def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hello"] = "Hello!"
        return context """

class UpdateProfileView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "email",
        "first_name",
        "last_name",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency"
    )
    success_message = "Profile updated"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["birthdate"].widget.attrs = {
            "placeholder": "Birthdate"
        }
        print(form)
        return form

class UpdatePasswordView(mixins.LoggedInOnlyView, SuccessMessageMixin, PasswordChangeView):

    template_name = "users/update-password.html"
    success_message = "Password Updated"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {
            "placeholder": "Current password"
        }
        form.fields["new_password1"].widget.attrs = {
            "placeholder": "New password"
        }
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "Confirm new password"
        }

        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()

@login_required
def switch_hosting(request):

    try:
        del request.session["is_hosting"]
    except KeyError:
        request.session["is_hosting"] = True
    return redirect(reverse("core:home"))