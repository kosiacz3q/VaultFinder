from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import VaultUser, VaultContest, UserActiveContest, VaultForm
from django.core.urlresolvers import reverse
from django.template import RequestContext
import random


@login_required
def index(request):
    """
    Generate main page.

    :param request: HttpRequest object
    :return: HttpResponse object with user and challenges info included
    """
    user_challenges = VaultContest.objects.filter(
        useractivecontest__user__user__username=request.user.username)

    vault_user = VaultUser.objects.get(user=request.user)

    return render_to_response("index.html", {
        'user': request.user,
        'vault': vault_user,
        'user_challenges': user_challenges,
        'ranking': VaultUser.objects.all()[:4],
        'has_public': True,
    }, RequestContext(request))


@login_required
def complete_challenge(request, challenge_id):
    """
    Mark challenge as completed and redirect to main page.

    :param request: HttpRequest object
    :param challenge_id: challenge's id
    :return: HttpResponseRedirect object
    """

    challenge_to_complete = get_object_or_404(UserActiveChallenge, challenge__pk=challenge_id)

    challenge_to_complete.completed = True
    challenge_to_complete.save()

    challenge_to_complete.user.exp += challenge_to_complete.challenge.exp;
    challenge_to_complete.user.save();

    return HttpResponseRedirect(reverse('vault:index'))


@login_required
def ranking(request):
    """
    Create ranking of users. Work only if logged user shares its statistics to the public.

    :param request: HttpRequest object
    :return: HttpResponse object with ranking dict
    """
    return render_to_response("ranking.html", {
        "items": VaultUser.objects.all(),
        "has_public": True,
    })


@login_required
def add_challenge(request):
    """
    Create add challenge form.

    :param request: HttpRequest object
    :return: HttpResponseRedirect object
    """
    if request.method == 'POST':
        form = VaultForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                # challenge = form.save(commit=False)
                # challenge.picture = form.cleaned_data['picture']
                # challenge.save()
                return HttpResponseRedirect('/')
            except:
                pass
    return render_to_response('addChallange.html', {'form': VaultForm()},
                              context_instance=RequestContext(request))


@login_required
def get_challenges(request):
    """
    Get five random challenges available for current user (ie. those which are assigned to current user's level
    and not already completed).

    :param request: HttpRequest object
    :return: HttpResponse object with drawn challenges
    """
    challenges = VaultContest.objects.filter(min_level__lte=request.user.vaultuser.level,
                                          max_level__gte=request.user.vaultuser.level)
    user_challenges = [i.challenge for i in UserActiveContest.objects.filter(user__exact=request.user.vaultuser)]
    challenges = [e for e in challenges if e not in user_challenges]
    random.shuffle(challenges)
    return render_to_response('newChallenge.html', {
        "items": challenges[:5]
    })


@login_required
def join_challenge(request, challenge_id):
    """
    Join user to challenge with given id.

    :param request: HttpRequest object
    :param challenge_id: id of challenge to which user wants to join
    :return: HttpResponse of index() method
    """
    _, created = UserActiveContest.objects.get_or_create(challenge=VaultContest.objects.get(pk=challenge_id),
                                                           user=VaultUser.objects.get(user=request.user))
    return HttpResponseRedirect(reverse('vault:index')) if created else HttpResponse("You already joined to this challenge.")
