from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from Accounts.models import User, Friends
from django.http import JsonResponse
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required


def Home(request):
    template = loader.get_template('first.html')
    return HttpResponse(template.render())


@login_required(login_url='login')
def Profile(request):
    template = loader .get_template('profile.html')
    player = request.user

    friends_as_user1 = Friends.objects.filter(user1=player)
    friends_as_user2 = Friends.objects.filter(user2=player)

    friends = []
    for friend in friends_as_user1:
        name = friend.user2.username
        games_won = friend.games_won_by_user1
        games_won_by_friend = friend.games_won_by_user2
        games_played = friend.games_played_between

        friends.append({
            'name': name,
            'games_won': games_won,
            'games_won_by_friend': games_won_by_friend,
            'games_played': games_played
        })

    for friend in friends_as_user2:
        name = friend.user1.username
        games_won = friend.games_won_by_user2
        games_won_by_friend = friend.games_won_by_user1
        games_played = friend.games_played_between

        friends.append({
            'name': name,
            'games_won': games_won,
            'games_won_by_friend': games_won_by_friend,
            'games_played': games_played
        })


    wp = int((player.games_won/player.games_played)*100) if(player.games_played>0) else " - "
    print(player,wp)
    context = {
        'user': player,
        'wp' : wp,
        'friend_list': friends,
    }
    return HttpResponse(template.render(context, request))

def add_friend(request, name):
    player = request.user
    friend = User.objects.filter(username=name).first()
    pair = Friends.objects.filter((Q(user1 = player) & Q(user2 = friend)) | (Q(user1 = friend) & Q(user2 = player))).first()

    if friend:
        if(pair):
            response_data = {'success': False, 'message': 'Friend already exists.' }
        else:
            Friends.objects.create(user1=player, user2=friend)
            print("success")
            response_data = {'success': True,'message': 'Friend added successfully!'}
    else:
        response_data = {'success': False, 'message': 'Invalid username. Friend not found.'}

    print(response_data)
    print(type(response_data))
    return JsonResponse(response_data)