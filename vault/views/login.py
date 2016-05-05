from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login


def login(request):
    return render(request, 'vault/login.html', {})


def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            return render(request, 'vault/vault.html', {})
        else:
            return render(request, 'vault/vault.html', {})
    else:
        return render(request, 'vault/vault.html', {})
        # Return an 'invalid login' error message.
