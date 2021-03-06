from django.contrib import admin
from custom_user.admin import EmailUserAdmin
from .models import *


class UserAdmin(EmailUserAdmin):
    pass


# Register your models here.
# admin.site.register(User)
admin.site.register(User, UserAdmin)
admin.site.register(OverseerContest)
admin.site.register(Sponsor)
admin.site.register(Enrollment)
admin.site.register(Duel)
admin.site.register(Round)
