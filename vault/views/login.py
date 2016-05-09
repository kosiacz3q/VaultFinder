from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate, login
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponseRedirect, Http404


def login_view(request):
    return context_login(request, {})


def context_login(request, context):
    login_form = UserLoginForm(request.POST or None)
    create_user_form = SpecialUserCreationForm(request.POST or None)

    context.update({
        'user_login_form': login_form,
        'user_create_form': create_user_form,
    })
    return render(request, 'vault/login.html', context)


def auth_view(request):

    if not request.method == 'POST':
        return Http404()

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)

    if (user is not None) and user.is_active:
        login(request, user)
        return HttpResponseRedirect('vault')

    return context_login(request, {'login_error_message': "Invalid username or password."})


def create_user_view(request):

    if not request.method == 'POST':
        return Http404()

    username = request.POST.get('username', '')
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')

    if not password1 == password2:
        return context_login(request, {'create_error_message': "passwords mismatch"})

    user = User.objects.create_user(
        username=username,
        email='unknown@mail.com',
        password=password1)

    user.save()

    return HttpResponseRedirect('/vault')


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(required=True, max_length=30)
    password = forms.PasswordInput()


class SpecialUserCreationForm(UserCreationForm):
    username = forms.CharField(required=True, max_length=30)
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

