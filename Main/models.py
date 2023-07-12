# from django.db import models
# Position =[[0 for i in range(6)]for j in range(9)]
# Move = 0
# Create your models here.
# class Position(models.Model):
#     data = models.JSONField(default=[[0 for i in range(6)]for j in range(9)])

from django.db import models

# class Position(models.Model):
#     # define the fields of the model
#     data = models.JSONField(null=True)

#     # define a string representation for the model
#     def __str__(self):
#         return str(self.data)

# class Move(models.Model):
#     move = models.IntegerField()

pos_dict = {}

def get_position(session_id):
    if session_id in pos_dict:
        return pos_dict[session_id]
    else:
        return [[0]*6 for i in range(9)]

def set_position(session_id, position_array):
    pos_dict[session_id] = position_array

