from django.contrib import admin
from .models import ChallengeQueue, FriendlyChQueue, RunningChallenge


admin.site.register(ChallengeQueue)
admin.site.register(FriendlyChQueue)
admin.site.register(RunningChallenge)
