from django.shortcuts import render_to_response, redirect, render
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import OverseerContest, Enrollment, Sponsor, User, Duel, Round
from .forms import EnrollForm, OverseerContestForm, DuelForm, SponsorForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import random


def index(request):
    paginator = Paginator(OverseerContest.objects.all(), 10)
    page = request.GET.get('page')
    try:
        overseers = paginator.page(page)
    except PageNotAnInteger:
        overseers = paginator.page(1)
    except EmptyPage:
        overseers = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {'overseers': overseers})


def detail(request, overseer_id, force=0):
    overseer_contest = OverseerContest.objects.get(id=overseer_id)
    count = Enrollment.objects.filter(overseer_contest=overseer_contest).count()
    enrolled = Enrollment.objects.filter(overseer_contest__pk=overseer_id, user__id=request.user.id).count()

    if force:
        OverseerContest.objects.filter(pk=overseer_contest.pk).update(in_progress=False)

    if count == overseer_contest.limit and not overseer_contest.in_progress:
        participants = [e.user for e in Enrollment.objects.filter(overseer_contest=overseer_contest).order_by('-ranking')]
        Duel.random_matches(participants, overseer_contest)
        OverseerContest.objects.filter(pk=overseer_contest.pk).update(in_progress=True)

    return render(request, "detail.html",
                  {"overseer_contest": overseer_contest,
                   "count": count,
                   "enrolled": enrolled,
                   "enrollments": Enrollment.objects.filter(overseer_contest=overseer_contest),
                   "matches": Duel.objects.filter(round__overseer_contest=overseer_contest).order_by('round__name'),
                   "bracket": Duel.generate_json(overseer_contest)})


@login_required(login_url=reverse_lazy('auth_login'))
def join(request, overseer_id):
    if request.method == "POST":
        form = EnrollForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.overseer_contest = OverseerContest.objects.get(pk=overseer_id)
            post.save()
            return redirect('contest:detail', overseer_id=overseer_id)
    else:
        form = EnrollForm()
    return render(request, 'enroll.html', {'form': form,
                                           'overseer_id': overseer_id})


@login_required(login_url=reverse_lazy('auth_login'))
def create(request):
    if request.method == "POST":
        form = OverseerContestForm(request.POST)
        if form.is_valid():
            overseer = form.save(commit=False)
            overseer.organizer = request.user
            overseer.save()
            form.save_m2m()
            return redirect('contest:index')
    else:
        form = OverseerContestForm()
    return render(request, 'create.html', {'form': form,
                                           'label': 'Create Overseer Contest'})


@login_required(login_url=reverse_lazy('auth_login'))
def edit(request, overseer_id):
    overseer = OverseerContest.objects.filter(id=overseer_id)
    if not overseer:
        return HttpResponse("OverseerContest not exist!")
    if overseer[0].organizer != request.user:
        return HttpResponse("It's not your overseer_contest!")
    if request.method == "POST":
        form = OverseerContestForm(request.POST, instance=overseer[0])
        if form.is_valid():
            form.save()
            return redirect('contest:index')
    else:
        form = OverseerContestForm(instance=overseer[0])

    return render(request, 'create.html', {'form': form,
                                           'label': 'Edit overseer contest'})


@login_required(login_url=reverse_lazy('auth_login'))
def update_duel(request, duel_id):

    duel = Duel.objects.filter(id=duel_id)[0] if Duel.objects.filter(id=duel_id) else None

    if not duel:
        return HttpResponse("Duel not exist!")

    if duel.player_1 != request.user and duel.player_2 != request.user:
        return HttpResponse("It's not your duel!")

    if duel.last_filled == request.user:
        return HttpResponse("You already fill!")

    if request.method == "POST":
        form = DuelForm(request.POST, instance=duel)
        if form.is_valid():
            duel = form.save(commit=False)
            duel.last_filled = request.user
            duel.save()
            return redirect('contest:index')
    else:
        form = DuelForm(instance=duel)
    return render(request, 'create.html', {'form': form,
                                           'label': 'Update duel'})


def search(request):
    if request.GET and request.GET['query']:
        paginator = Paginator(OverseerContest.objects.filter(name__contains=request.GET['query']), 10)
        page = request.GET.get('page')
        try:
            tournaments = paginator.page(page)
        except PageNotAnInteger:
            tournaments = paginator.page(1)
        except EmptyPage:
            tournaments = paginator.page(paginator.num_pages)
        return render(request, 'index.html', {'overseers': tournaments})
    else:
        return redirect('contest:index')


@login_required(login_url=reverse_lazy('auth_login'))
def add_sponsor(request):
    if request.method == "POST":
        form = SponsorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contest:index')
    else:
        form = SponsorForm()
    return render(request, 'sponsor.html', {'form': form})