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
        overseers = paginator.page(page)
    except PageNotAnInteger:
        overseers = paginator.page(1)
    except EmptyPage:
        overseers = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {'overseers': overseers})


def detail(request, overseer_id, force=0):
    overseer = Tournament.objects.get(id=overseer_id)
    count = Enrollment.objects.filter(overseer=overseer).count()
    enrolled = Enrollment.objects.filter(overseer__pk=overseer_id, user__id=request.user.id).count()

    if force:
        Tournament.objects.filter(pk=overseer.pk).update(in_progress=False)

    if count == overseer.limit and not overseer.in_progress:
        teams = [e.user for e in Enrollment.objects.filter(overseer=overseer).order_by('-ranking')]
        Match.random_matches(teams, overseer)
        Tournament.objects.filter(pk=overseer.pk).update(in_progress=True)

    return render(request, "detail.html",
                  {"overseer": overseer,
                   "count": count,
                   "enrolled": enrolled,
                   "enrollments": Enrollment.objects.filter(overseer=overseer),
                   "matches": Match.objects.filter(round__overseer=overseer).order_by('round__name'),
                   "bracket": Match.generate_json(overseer)})


@login_required(login_url=reverse_lazy('auth_login'))
def join(request, overseer_id):
    if request.method == "POST":
        form = EnrollForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.overseer = Tournament.objects.get(pk=overseer_id)
            post.save()
            return redirect('contest:detail', overseer_id=overseer_id)
    else:
        form = EnrollForm()
    return render(request, 'enroll.html', {'form': form,
                                           'overseer_id': overseer_id})


@login_required(login_url=reverse_lazy('auth_login'))
def create(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            overseer = form.save(commit=False)
            overseer.organizer = request.user
            overseer.save()
            form.save_m2m()
            return redirect('contest:index')
    else:
        form = TournamentForm()
    return render(request, 'create.html', {'form': form,
                                           'label': 'Create overseer'})


@login_required(login_url=reverse_lazy('auth_login'))
def edit(request, overseer_id):
    overseer = Tournament.objects.filter(id=overseer_id)
    if not overseer:
        return HttpResponse("Tournament not exist!")
    if overseer[0].organizer != request.user:
        return HttpResponse("It's not your overseer!")
    if request.method == "POST":
        form = TournamentForm(request.POST, instance=overseer[0])
        if form.is_valid():
            form.save()
            return redirect('contest:index')
    else:
        form = TournamentForm(instance=overseer[0])

    return render(request, 'create.html', {'form': form,
                                           'label': 'Edit overseer'})


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
            return redirect('contest:index')
    else:
        form = MatchForm(instance=match)
    return render(request, 'create.html', {'form': form,
                                           'label': 'Update match'})
