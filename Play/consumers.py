# from channels.generic.websocket import WebsocketConsumer
# from asgiref.sync import async_to_sync
# import json


# class GameRoom(WebsocketConsumer):
    
#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_code']
#         self.room_group_name = 'room_%s' % self.room_name
#         print(self.room_group_name)

#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )

#         self.accept()

#     def disconnect(self):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )
    
#     def receive(self, text_data):
#         print(text_data)
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,{
#                 'type' : 'position_update',
#                 'payload' : text_data
#             }
#         )
    
#     def position_update(self, event):
#         data = event['payload']
#         data =json.loads(data)

#         self.send(text_data= json.dumps({
#             'payload' : data['data']
#         }))



#########################################################

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameRoom(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.group_name = "Play_%s" % self.room_code

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chatbox_message",
                "message": message,
                "username": username,
            },
        )
    # Receive message from room group.
    async def chatbox_message(self, event):
        message = event["message"]
        username = event["username"]
        #send message and username of sender to websocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                }
            )
        )

    pass