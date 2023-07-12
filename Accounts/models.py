
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='custom_user_set')

class Friends(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_as_user2')
    games_played_between = models.IntegerField(default=0)
    games_won_by_user1 = models.IntegerField(default=0)
    games_won_by_user2 = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user1', 'user2']  # Ensure uniqueness of friendships
