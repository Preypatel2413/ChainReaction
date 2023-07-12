from django.db import models
from Accounts.models import User
# Create your models here.

pos_dict = {}

def get_position(id):
    if id in pos_dict:
        return pos_dict[id]
    else:
        return [[0]*6 for i in range(9)]

def set_position(id, position_array):
    pos_dict[id] = position_array



class ChallengeQueue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class RunningChallenge(models.Model):
    player1 = models.ForeignKey(User, related_name='player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='player2', on_delete=models.CASCADE)
    room_name = models.CharField(max_length=8)

    class Meta:
        unique_together = ['player1', 'player2']