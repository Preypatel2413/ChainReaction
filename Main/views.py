from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
# from .models import Position
# from .models import Move
from .models import get_position, set_position,pos_dict

invalid = False
def Main(request):
    session_id = request.session.session_key
    if session_id in pos_dict.keys():
        position_array = get_position(session_id)
    else:
        request.session.save()
        session_id = request.session.session_key
        position_array = [[0]*6 for i in range (9)]
        set_position(session_id, position_array)
    # print(session_id)
    # print(pos_dict)
    template = loader.get_template('MainGame.html')
    context = {
        'Position' : position_array,
        'move' : mv(session_id),
        'win' : win(session_id),
    }
    return HttpResponse(template.render(context,request))


def update_position(request, row, col):
    # position = Position  # Get the first instance of the Position model
    session_id =request.session.session_key
    # print(session_id)
    position = pos_dict[session_id]
    move = mv(session_id)
    # print(move)
    # Update the position array element
    if (move%2==0):
        if (position[row][col]<0):
            pass
            # print("invalid move")
            # return False
            # return HttpResponse(position[row][col])
            # continue
        add(row,col,1,session_id)
    else:
        if (position[row][col]>0):
            pass
            # print("invalid move")
            # return False
            # return HttpResponse(position[row][col])
            # continue
        add(row,col,-1,session_id)
    
    # if move>=2:
    #     win(session_id)
            # show()
            # break
    
        # print(position)
    # Save the updated position array to the database
    # position.data = position_array
    # position.save()

    return HttpResponse()

######################################################
def clear_data(request):
    id = request.session.session_key
    # print("call")
    position = pos_dict[id]
    for i in range(rows):
        for j in range(columns):
            position[i][j] = 0
    
    return HttpResponse()
    
######################################################
columns = 6
rows = 9

def mv(request):
    session_id = request
    position = pos_dict[session_id]
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
    session_id = id
    position = pos_dict[session_id]
    # position = Position
    position[row][col] = 0
    add(row-1,col,player,id)
    add(row+1,col,player,id)
    add(row,col-1,player,id)
    add(row,col+1,player,id)


def add(row,col,player,id):
    session_id = id
    position = pos_dict[session_id]
    # position = Position

    if(row<0 or row>=rows or col<0 or col>=columns):
        return None
    if(position[row][col] == 0):
        position[row][col] = player
    elif(abs(position[row][col]) < mx(row,col)):
        position[row][col] = (abs(position[row][col])+1)*player
    else:
        reaction(row,col,player,id)


def win(request):
    session_id = request
    position = pos_dict[session_id]
    # position = Position

    if mv(request)<=2:
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
        # print("Player 2 has won!!")
        return 2
    elif(p2==0):
        # print("Player 1 has won!!")
        return 1
    
    return False