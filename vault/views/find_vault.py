from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


#  @login_required(login_url='/vault/')
def find_vault(request):

    current_user = "p" + request.user.username

    if request.user.is_authenticated():
        current_user += " is authenticated"

    context0 = "test context"

    return render(request, 'vault/vault.html', {
        'current_user': ("|" + current_user + "|"),
        'test_context': context0,
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/vault/')
