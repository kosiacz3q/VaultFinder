from django.shortcuts import render_to_response, redirect, render
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Tournament, Enrollment, Sponsor, User, Match, Round
from .forms import EnrollForm, TournamentForm, MatchForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import random


# Create your views here.

def index(request):
    paginator = Paginator(Tournament.objects.all(), 10)
    page = request.GET.get('page')
    try:
        aisites = paginator.page(page)
    except PageNotAnInteger:
        aisites = paginator.page(1)
    except EmptyPage:
        aisites = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {'aisites': aisites})


def detail(request, aisite_id, force=0):
    aisite = Tournament.objects.get(id=aisite_id)
    count = Enrollment.objects.filter(aisite=aisite).count()
    enrolled = Enrollment.objects.filter(aisite__pk=aisite_id, user__id=request.user.id).count()

    if force:
        Tournament.objects.filter(pk=aisite.pk).update(in_progress=False)

    if count == aisite.limit and not aisite.in_progress:
        teams = [e.user for e in Enrollment.objects.filter(aisite=aisite).order_by('-ranking')]
        Match.random_matches(teams, aisite)
        Tournament.objects.filter(pk=aisite.pk).update(in_progress=True)

    return render(request, "detail.html",
                  {"aisite": aisite,
                   "count": count,
                   "enrolled": enrolled,
                   "enrollments": Enrollment.objects.filter(aisite=aisite),
                   "matches": Match.objects.filter(round__aisite=aisite).order_by('round__name'),
                   "bracket": Match.generate_json(aisite)})


@login_required(login_url=reverse_lazy('auth_login'))
def join(request, aisite_id):
    if request.method == "POST":
        form = EnrollForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.aisite = Tournament.objects.get(pk=aisite_id)
            post.save()
            return redirect('football:detail', aisite_id=aisite_id)
    else:
        form = EnrollForm()
    return render(request, 'enroll.html', {'form': form,
                                           'aisite_id': aisite_id})


@login_required(login_url=reverse_lazy('auth_login'))
def create(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            aisite = form.save(commit=False)
            aisite.organizer = request.user
            aisite.save()
            form.save_m2m()
            return redirect('football:index')
    else:
        form = TournamentForm()
    return render(request, 'create.html', {'form': form,
                                           'label': 'Create aisite'})


@login_required(login_url=reverse_lazy('auth_login'))
def edit(request, aisite_id):
    aisite = Tournament.objects.filter(id=aisite_id)
    if not aisite:
        return HttpResponse("Tournament not exist!")
    if aisite[0].organizer != request.user:
        return HttpResponse("It's not your aisite!")
    if request.method == "POST":
        form = TournamentForm(request.POST, instance=aisite[0])
        if form.is_valid():
            form.save()
            return redirect('football:index')
    else:
        form = TournamentForm(instance=aisite[0])

    return render(request, 'create.html', {'form': form,
                                           'label': 'Edit aisite'})


@login_required(login_url=reverse_lazy('auth_login'))
def update_match(request, match_id):
    match = Match.objects.filter(id=match_id)[0] if Match.objects.filter(id=match_id) else None
    if not match:
        return HttpResponse("Match not exist!")
    if match.player_1 != request.user and match.player_2 != request.user:
        return HttpResponse("It's not your match!")
    # fill = match.fill_1 if match.player_2 == request.user else match.fill_2
    if match.last_filled == request.user:
        return HttpResponse("You already fill!")
    if request.method == "POST":
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save(commit=False)
            match.last_filled = request.user
            match.save()
            return redirect('football:index')
    else:
        form = MatchForm(instance=match)
    return render(request, 'create.html', {'form': form,
                                           'label': 'Update match'})
