from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


#@login_required(login_url='/vault/')
def find_vault(request):
    return render(request, 'vault/vault.html', {})


def logout_view(request):
    logout(request)
