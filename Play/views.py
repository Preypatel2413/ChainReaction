from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from Accounts.models import Friends
from .models import ChallengeQueue, RunningChallenge
from .models import get_position, set_position, pos_dict
import time, random, string

pairing = False
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

    context = {
        'friends': friends,
        'pairing': pairing
    }
    return HttpResponse(template.render(context, request))

def acceptChallenge(request, index):

    pass

def createChallenge(request, index):
    print("HIIIII")
    pass

def randomChallenge(request):
    current_user = request.user
    challenge_queue = ChallengeQueue.objects.all().order_by('timestamp')
    
    if challenge_queue.exists():
        opponent = challenge_queue.first().user
        challenge_queue.first().delete()
        room_code = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        RunningChallenge.objects.create(player1=opponent, player2=current_user, room_name = room_code)

        if current_user in pos_dict.keys():
            position_array = get_position(current_user)
        else:
            position_array = [[0]*6 for i in range (9)]
            set_position(current_user, position_array)
            set_position(opponent, position_array)
        
        print("Player1 redirected")
        print(pos_dict)
        return redirect('/Play/' + room_code+'/')
    else:
        ChallengeQueue.objects.create(user=current_user)
        global pairing 
        pairing = True
        while pairing:
            time.sleep(0.5)  # Delay for 0.5 second before checking again
            matches = RunningChallenge.objects.all()
            for match in matches:
                if match.player1 == current_user or match.player2 == current_user:
                    print("player2 redirected")
                    print(pos_dict)
                    room_code = match.room_name
                    return redirect('/Play/' + room_code+'/')


def endWait(request):
    current_user = request.user
    challenge_queue = ChallengeQueue.objects.filter(user=current_user)
    if challenge_queue.exists():
        challenge_queue.delete()
    global pairing 
    pairing = False
    response = {'pairing': False}
    return JsonResponse(response)

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
def Play(request, room_code):
    id = request.user
    if id in pos_dict.keys():
        position_array = get_position(id)
    else:
        position_array = [[0]*6 for i in range (9)]
        set_position(id, position_array)
    print(id)
    print(pos_dict)
    context = {
        'Position' : position_array,
        'move' : mv(id),
        'win' : win(id),
        'room_code': room_code,
    }
    template = loader.get_template('Multiplayer.html')
    return HttpResponse(template.render(context,request))


def update_position_(request, row, col):
    # position = Position  # Get the first instance of the Position model
    id = request.user
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
    
    return False

######################################################
def clear_data(request):
    id = request.session.session_key
    print("call")
    position = pos_dict[id]
    for i in range(rows):
        for j in range(columns):
            position[i][j] = 0
    
######################################################