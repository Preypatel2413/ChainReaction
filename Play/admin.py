from django.contrib import admin
from .models import ChallengeQueue, RunningChallenge


admin.site.register(ChallengeQueue)
admin.site.register(RunningChallenge)
