from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from Accounts.models import User, Friends
from .models import ChallengeQueue, FriendlyChQueue, RunningChallenge
from .models import get_position, set_position, pos_dict, set_chat, chat_diary
import time, random, string
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# from django.contrib.auth.models import User
# from Accounts.models import User
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def Challenge(request):
    template = loader.get_template('Challenges.html')

    current_user = request.user

    friends_as_user1 = Friends.objects.filter(user1=current_user)
    friends_as_user2 = Friends.objects.filter(user2=current_user)

    friends = []
    for friend in friends_as_user1:
        friend_name = friend.user2.username
        games_won_by_X = friend.games_won_by_user1
        games_won_by_opponent = friend.games_won_by_user2
        games_played = friend.games_played_between

        friends.append({
            'friend_name': friend_name,
            'games_won_by_X': games_won_by_X,
            'games_won_by_opponent': games_won_by_opponent,
            'games_played': games_played
        })

    for friend in friends_as_user2:
        friend_name = friend.user1.username
        games_won_by_X = friend.games_won_by_user2
        games_won_by_opponent = friend.games_won_by_user1
        games_played = friend.games_played_between

        friends.append({
            'friend_name': friend_name,
            'games_won_by_X': games_won_by_X,
            'games_won_by_opponent': games_won_by_opponent,
            'games_played': games_played
        })
    
    friendly_challenge_queue = FriendlyChQueue.objects.filter(p2 = current_user).order_by('timestamp')
    
    context = {
        'friends': friends,
        'received_challenges': friendly_challenge_queue,
    }
    return HttpResponse(template.render(context, request))

##---------------------------------------------------------------------------------------------------------------------##

def createChallenge(request, name):
    current_user = request.user
    opponent = User.objects.get(username = name)
    
    FriendlyChQueue.objects.create(p1=current_user, p2 = opponent)
    response_data = {'pairing_z': True}
    print(response_data)
    print("Challenge created for", current_user, name)
    return HttpResponse(json.dumps(response_data), content_type = 'application/json')


def acceptChallenge(request, name):
    opponent = User.objects.get(username = name)
    current_user = request.user
    
    opponent_queue = FriendlyChQueue.objects.filter(p1 = opponent).order_by('timestamp')
    opponent_queue.delete()
    user_queue = FriendlyChQueue.objects.filter(Q(p1 = current_user) | Q(p2 = current_user)).order_by('timestamp')
    user_queue.delete()
    room_code = ''.join(random.choice(string.ascii_letters) for _ in range(8))
    RunningChallenge.objects.create(player1=opponent, player2=current_user, room_name=room_code)

    if current_user in pos_dict.keys():
        position_array = get_position(current_user)
    else:
        position_array = [[0] * 6 for _ in range(9)]
        set_position(current_user, position_array)
        set_position(opponent, position_array)
        cht = []                ##
        set_chat(current_user, cht)         ##
        set_chat(opponent, cht)             ##
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'random_challenge',
        {
            'type': 'game_state_update',
            'message': 'You have been paired with another player.',
            'player1_name': opponent.username,
            'player2_name': current_user.username,
            'room_code' : room_code
        }
    )

    print("redirecting Player 2")
    return redirect('/Game/' + room_code + '/')
    


def randomChallenge(request):
    current_user = request.user
    challenge_queue = ChallengeQueue.objects.all().order_by('timestamp')

    if challenge_queue.exists():
        opponent = challenge_queue.first().user
        challenge_queue.first().delete()
        room_code = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        RunningChallenge.objects.create(player1=opponent, player2=current_user, room_name=room_code)

        if current_user in pos_dict.keys():
            position_array = get_position(current_user)
        else:
            position_array = [[0] * 6 for _ in range(9)]
            set_position(current_user, position_array)
            set_position(opponent, position_array)
            cht = []                ##
            set_chat(current_user, cht)         ##
            set_chat(opponent, cht)             ##

        # Send message to the other player's WebSocket
        print(opponent.username, room_code)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'random_challenge',
            {
                'type': 'game_state_update',
                'message': 'You have been paired with another player.',
                'player1_name': opponent.username,
                'player2_name': current_user.username,
                'room_code' : room_code
            }
        )

        print("redirecting Player 2")
        return redirect('/Game/' + room_code + '/')
    else:
        ChallengeQueue.objects.create(user=current_user)
        

        # Update the HTML template to display the endWait button instead of randomChallenge button
        template = loader.get_template('Challenges.html')
        # context = {
        #     'pairing': pairing
        # }
        response_data = {'pairing': True}
        print(response_data)
        print("response to player1")
        return HttpResponse(json.dumps(response_data), content_type = 'application/json')
        

def endWait(request,index):
    current_user = request.user
    if(index == -1):
        challenge_queue = ChallengeQueue.objects.filter(user=current_user)
        if challenge_queue.exists():
            challenge_queue.delete()

        response_data = {'pairing': False}
        return HttpResponse(json.dumps(response_data), content_type = 'application/json')
    else:
        pass

def createMatch(request):
    if session_id in pos_dict.keys():
        position_array = get_position(session_id)
    else:
        request.session.save()
        session_id = request.session.session_key
        position_array = [[0]*6 for i in range (9)]
        set_position(session_id, position_array)


#----------------------------------------Multiplayer---------------------------------------------------#

invalid = False
@login_required(login_url='login')
def Game(request, room_code):
    id = request.user
    if id in pos_dict.keys():
        position_array = get_position(id)
    else:
        position_array = [[0]*6 for i in range (9)]
        set_position(id, position_array)
    print(id)
    print(pos_dict)

    q = RunningChallenge.objects.filter(Q(player1 = id) | Q(player2 = id))
    if(id == q.first().player1):
        player = 0
        oppnt = q.first().player2
    else:
        player = 1
        oppnt = q.first().player1

    context = {
        'Position' : position_array,
        'move' : mv(id),
        'win' : win(id),
        'room_code': room_code,
        'p' : player,
        'user' : id,
        'opponent' : oppnt,
        'diary' : chat_diary[id]
    }
    template = loader.get_template('Multiplayer.html')
    return HttpResponse(template.render(context,request))


def update_position_(request, row, col):
    # position = Position  # Get the first instance of the Position model
    id = request.user
    room_code = -1
    rooms1 = RunningChallenge.objects.filter(player1=id) 
    rooms2 = RunningChallenge.objects.filter(player2=id)
    for room in rooms1:
        if(room_code ==-1):
            room_code = room.room_name
    for room in rooms2:
        if(room_code ==-1):
            room_code = room.room_name

    print(id)
    position = pos_dict[id]
    move = mv(id)
    # print(move)
    # Update the position array element
    if (move%2==0):
        if (position[row][col]<0):
            print("invalid move")
            # return False
            return HttpResponse(position[row][col])
            # continue
        add(row,col,1,id)
    else:
        if (position[row][col]>0):
            print("invalid move")
            # return False
            return HttpResponse(position[row][col])
            # continue
        add(row,col,-1,id)
    
    if move>=2:
        win(id)
            # show()
            # break
    
        print(position)
    # Save the updated position array to the database
    # position.data = position_array
    # position.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'game_' + room_code,
        {
            'type': 'position_update',
            'message': 'update',
            'row': row,
            'col': col,
        }
    )
    return HttpResponse(position[row][col])



columns = 6
rows = 9

def mv(id):
    position = pos_dict[id]
    sum=0
    for i in range(rows):
        for j in range(columns):
            sum+= abs(position[i][j])
    
    return sum


def mx(row,col):
    if((row==0 or row==rows-1) and (col==0 or col==columns-1)):
        return 1
    elif((row==0 or row==rows-1) or (col==0 or col==columns-1)):
        return 2
    else:
        return 3

def reaction(row,col,player, id):
    
    position = pos_dict[id]
    # position = Position
    position[row][col] = 0
    add(row-1,col,player,id)
    add(row+1,col,player,id)
    add(row,col-1,player,id)
    add(row,col+1,player,id)


def add(row,col,player,id):
    
    position = pos_dict[id]
    # position = Position

    if(row<0 or row>=rows or col<0 or col>=columns):
        return None
    if(position[row][col] == 0):
        position[row][col] = player
    elif(abs(position[row][col]) < mx(row,col)):
        position[row][col] = (abs(position[row][col])+1)*player
    else:
        reaction(row,col,player,id)


def win(id):
    
    position = pos_dict[id]
    # position = Position

    if mv(id)<=2:
        return False

    p1=0
    p2=0
    for i in range(rows):
        for j in range(columns):
            if (position[i][j] > 0):
                p1+=1
            elif(position[i][j] < 0):
                p2+=1
    
    if(p1==0):
        print("Player 2 has won!!")
        return 2
    elif(p2==0):
        print("Player 1 has won!!")
        return 1
    
    return -1

######################################################
def clearGame(request,win,p):
    id = request.user
    player = request.user.username
    print("call")
    position = pos_dict[id]
    for i in range(rows):
        for j in range(columns):
            position[i][j] = 0
    
    del chat_diary[id]
    
    user = get_object_or_404(User, username=player)

    user.games_played += 1

    if(p + 1 == win):
        user.games_won += 1

    user.save()

    if(p==0):
        gm = RunningChallenge.objects.filter(player1 = id)
        opnt = gm.first().player2
        gm.delete()

        pair = Friends.objects.filter((Q(user1 = id) & Q(user2 = opnt)) | (Q(user1 = opnt) & Q(user2 = id))).first()
        if(pair is not None):
            pair.games_played_between += 1
            if(win == 1):
                if(pair.user1 == id):
                    pair.games_won_by_user1 +=1
                else:
                    pair.games_won_by_user2 +=1
            elif(win==2):
                if(pair.user1 == id):
                    pair.games_won_by_user2 +=1
                else:
                    pair.games_won_by_user1 +=1
            
            pair.save() 

    return HttpResponse()
######################################################

def send_Message(request, p, message):
    player = request.user

    chat_diary[player].append([p, str(player.username)[0], message])

    room_code = RunningChallenge.objects.filter(Q(player1=player) | Q(player2=player)).first().room_name

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'game_' + room_code,
        {
            'type': 'position_update',
            'message': 'update',
            'row': 0,
            'col': 0,
        }
    )

    return HttpResponse()


