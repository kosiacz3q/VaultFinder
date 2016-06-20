from django.db import models
from custom_user.models import AbstractEmailUser
from django.conf import settings
from django.dispatch import receiver
from registration.signals import user_registered
from django.db.models import signals, Max
import random
from model_utils import FieldTracker
from django.db.models import Q


class Sponsor(models.Model):
    name = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='upload/', default='default.jpg')

    def __str__(self):
        return self.name


class User(AbstractEmailUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class OverseerContest(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    deadline = models.DateTimeField()
    date = models.DateTimeField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    sponsors = models.ManyToManyField(Sponsor, blank=True)
    limit = models.IntegerField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL)
    in_progress = models.BooleanField(default=False)
    round_number = models.IntegerField(default=0)

    def __str__(self):
        return "%s (%s)" % (self.name, self.description)


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    overseer_contest = models.ForeignKey(OverseerContest)
    ranking = models.IntegerField(unique=True)
    license_id = models.IntegerField(unique=True)

    def __str__(self):
        return "%s joined %s" % (self.user, self.overseer_contest.name)


@receiver(user_registered)
def user_registered_handler(sender, user, request, **kwargs):
    user.first_name = request.POST.get('first_name')
    user.last_name = request.POST.get('last_name')
    user.save()


class Round(models.Model):
    overseer_contest = models.ForeignKey(OverseerContest)
    name = models.IntegerField(blank=False, default=1)
    # seeded = models.BooleanField()


class Duel(models.Model):
    round = models.ForeignKey(Round, related_name="round")
    player_1 = models.ForeignKey(User, related_name="player_1")
    player_2 = models.ForeignKey(User, related_name="player_2")
    winner = models.ForeignKey(User, null=True, blank=True, related_name="winner")
    score = models.CharField(max_length=5, null=False, default="-")
    tracker = FieldTracker()
    last_filled = models.ForeignKey(User, related_name="last_filled", null=True, blank=True)
    next_duel = models.ForeignKey('self', related_name="later_duel", null=True, blank=True)

    def __str__(self):
        return "round %d: %s - %s" % (
            self.round.name, self.player_1.first_name, self.player_2.first_name)

    @classmethod
    def generate_json(cls, overseer_contest):
        results = []
        json_duels = []

        _round = Duel.objects.filter(round__overseer_contest=overseer_contest).aggregate(Max('round__name'))['round__name__max']

        if _round:
            for r in range(1, _round + 1):
                duels = Duel.objects.filter(round__name=str(r), round__overseer_contest=overseer_contest)
                scores = []

                for m in duels:
                    if r == 1:
                        left = "TBA" if m.player_1 is None else (m.player_1.first_name + m.player_1.email)
                        right = "TBA" if m.player_2 is None else (m.player_2.first_name + m.player_2.email)
                        json_duels.append([left, right])

                    real_score = [0,0]

                    if m.score == "-":
                        m.score = "0:0"

                    if m.winner is not None:
                        real_score = m.score.split(':')

                    scores += [[int(real_score[0]), int(real_score[1])]]

                if len(scores) > 0:
                    results += [scores]

        return str({'teams': json_duels, 'results': results})

    @classmethod
    def random_matches(cls, participators, overseer_contest):
        new_round = Round()
        new_round.overseer_contest = overseer_contest

        new_round.name = overseer_contest.round_number + 1
        new_round.save()
        contest_participators = participators

        while len(contest_participators) > 1:
            participant = random.choice(contest_participators)

            while True:
                opponent = random.choice(contest_participators)
                if participant != opponent:
                    break

            match = Duel.objects.create(round=new_round,
                                         player_1=participant,
                                         player_2=opponent)

            match.save()

            if new_round.name != 1:
                Duel.objects.filter((Q(winner=opponent) | Q(winner=participant)) & Q(round__name=new_round.name - 1)).update(next_match=match)

            contest_participators.remove(opponent)
            contest_participators.remove(participant)

        if len(contest_participators) == 1:
            free = contest_participators[0]
            match = Duel.objects.create(round=new_round,
                                        player_1=free,
                                        player_2=free,
                                        score="1:0",
                                        winner=free)
            match.save()

        overseer_contest.round_number += 1
        overseer_contest.save()


def generate_overseer_bracket(sender, instance, created, **kwargs):
    if created or instance.tracker.previous('score') == '-':
        return

    if instance.tracker.has_changed('score') and instance.last_filled:
        sender.objects.filter(pk=instance.pk).update(winner=None,
                                                     score='-',
                                                     last_filled=None)
        return

    score = instance.score.split(':')

    if score[0] != '0' or score[1] != '0':
        winner = instance.player_1 if int(score[0]) > int(score[1]) else instance.player_2
        sender.objects.filter(pk=instance.pk).update(winner=winner)

    unfinished = sender.objects.filter(winner__isnull=True, round=instance.round)

    if unfinished.count() == 0:
        teams = [e.winner for e in Duel.objects.filter(round=instance.round)]

        if len(teams) == 1:
            return

        pairs = zip(teams[::2], teams[1::2])
        new_round = Round()
        new_round.overseer_contest = instance.round.overseer_contest
        new_round.name = instance.round.name + 1
        new_round.save()

        for player_1, player_2 in pairs:
            Duel.objects.create(round=new_round, player_1=player_1, player_2=player_2)


signals.post_save.connect(generate_overseer_bracket, sender=Duel)
