from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from math import log, floor
from django.db.models.signals import post_save
from django.forms import ModelForm


class VaultUser(models.Model):
    user = models.OneToOneField(User)

    strength = models.IntegerField(default=1)
    perception = models.IntegerField(default=1)
    endurance = models.IntegerField(default=1)
    charisma = models.IntegerField(default=1)
    intelligence = models.IntegerField(default=1)
    agility = models.IntegerField(default=1)
    luck = models.IntegerField(default=1)

    def __str__(self):
        """
        Return string representation of SpierdonUser object.
        """
        return self.user.__str__() + ' ' + self.level.__str__() + ' lvl'


def create_user_profile(sender, instance, created, **kwargs):
    """
    Create SpierdonUser object associated with newly created User.
    """
    if created:
        _, _ = VaultUser.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)


class VaultContest(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    date_start = models.DateField()
    date_end = models.DateField()

    creator = models.ForeignKey(VaultUser, null=False)

    picture = models.ImageField(upload_to='upload/', default='default.jpg')

    def __str__(self):
        """
        Return the string representation of VaultContest object.
        :return:
        """
        return "%s" % (self.name)


class UserActiveContest(models.Model):
    contest = models.ForeignKey(VaultContest, null=False)
    user = models.ForeignKey(VaultUser, null=False)

    def __str__(self):
        """
        Return the string representation of UserActiveChallenge object.
        """
        return "%s %s (completed: %s)" % (self.user, self.challenge, self.completed)


class VaultForm(ModelForm):
    class Meta:
        model = VaultContest
        fields = ['name', 'description', 'date_start', 'date_end', 'picture']
