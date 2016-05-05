from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate, login
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect


def login_view(request):
    return context_login(request, {})


def context_login(request, context):
    form = UserLoginForm(request.POST or None)
    context.update({'user_login_form': form})
    return render(request, 'vault/login.html', context)


def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            #
            return render(request, 'vault/vault.html', {})
        else:
            return context_login(request, {'error_message': "Invalid username or password."})
    else:
        return context_login(request, {'error_message': "Invalid username or password."})
        # Return an 'invalid login' error message.


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(required=True, max_length=30)
    password = forms.PasswordInput()

    class Meta:
        model = User
        fields = ("username", "password")
