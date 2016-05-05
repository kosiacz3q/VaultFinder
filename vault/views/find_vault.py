from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


@login_required(login_url='/vault/')
def find_vault(request):
    return render(request, 'vault/vault.html', {})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/vault/')
