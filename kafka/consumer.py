

import json
from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import YourModel
import requests


# ------------------------------------------------

# from django.shortcuts import render
# from django.http import JsonResponse
# from django.core.paginator import Paginator
from confluent_kafka import Consumer, KafkaException, KafkaError
import json

# from access_logs_producer_v2 import get_kafka_producer, fetch_oracle_data, send_to_kafka
# from .access_logs_producer_v2 import *

# from kafka_streaming.kafka.access_logs_producer_v2 import get_kafka_producer, fetch_oracle_data, send_to_kafka


from .access_logs_producer_v2 import get_kafka_producer, fetch_oracle_data, send_to_kafka


# Kafka Configuration
KAFKA_TOPIC = 'iB360_access_logs'
KAFKA_SERVERS = ['localhost:9092']

# --------------------------------------------------


# from asyncio import sleep

# class UpdatedDataConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = 'updated_data_group'
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         print('WebSocket connected...')
#         await self.accept()

#         # Start a background task to send periodic updates
#         self.keep_running = True
#         self.send_periodic_updates_task = self.channel_layer.loop.create_task(self.send_periodic_updates())

#     async def disconnect(self, close_code):
#         self.keep_running = False  # Stop the periodic updates loop
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#         print('WebSocket closed:', close_code)

#     async def receive(self, text_data):
#         print('Data from client:', text_data)
#         data = json.loads(text_data)
#         action = data.get('msg')
#         print('Message got from client: ', action)

#         if action == "get_updated_data":
#             updated_data = await self.get_updated_data()
#             await self.send(text_data=json.dumps(updated_data))

#     async def send_periodic_updates(self):
#         while self.keep_running:
#             updated_data = await self.get_updated_data()
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     "type": "websocket.message",
#                     "data": updated_data,
#                 }
#             )
#             await sleep(5)  # Check for updates every 5 seconds

#     async def websocket_message(self, event):
#         print('Data: ', event['data'])
#         await self.send(text_data=json.dumps(event["data"]))

#     async def get_updated_data(self):
        
#         response = requests.get('http://localhost:5500/data')
#         return {'data': json.loads(response.text)}
        














# ------------------------------------------------


class UpdatedDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept WebSocket connection
        self.room_group_name = 'updated_data_group'  # You can change this name to be unique

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print('WEb socket is working..................................')
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print('Web Closed: ', close_code)

    async def receive(self, text_data):
        # Receive message from WebSocket
        print('Data from Postman: ', text_data)
        data = json.loads(text_data)
        action = data.get('msg')
        

        # If you need to send updated data based on some action
        if action == "get_updated_data":
            updated_data = await self.get_updated_data()
            # Send the updated data to WebSocket
            await self.send(text_data=json.dumps(updated_data))

    async def send_updated_data(self):
        updated_data = await self.get_updated_data()
        # Send updated data to WebSocket group
        await self.send(text_data=json.dumps(updated_data))



    async def get_updated_data(self):
        try:
            # Initialize Kafka Consumer with Confluent Kafka Consumer
            consumer = Consumer({
                'bootstrap.servers': ','.join(KAFKA_SERVERS),
                'group.id': 'django_consumer_group',
                'auto.offset.reset': 'earliest',
            })

            # Subscribe to the Kafka topic
            consumer.subscribe([KAFKA_TOPIC])

            data = []  # Initialize an empty list to store messages

            # Consume messages from Kafka
            try:
                # for _ in range(999):  # Fetch up to 50 messages
                while True:
                    msg = consumer.poll(timeout=1.0)
                    if msg is None:
                        continue
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            continue
                        else:
                            raise KafkaException(msg.error())
                    else:
                        # Decode and parse the JSON data from Kafka
                        message_data = json.loads(msg.value().decode('utf-8'))
                        print('Message data from Kafka: ', message_data)
                        print('Data ID: ', message_data['ID'])
                        data.append(message_data)
                        if(message_data['ID'] == 1):
                            break

            except KafkaException as e:
                print(f"Kafka error: {e}")
                return {'data': data}  # Directly return the Python list

            finally:
                # Ensure the consumer is closed after fetching the required records
                consumer.close()

            # Return the fetched data
            print("Fetched Kafka Data:", data)  # Debugging
            return {'data': data}  # Return the list directly, no need for json.loads()

        except Exception as e:
            print(f"Error consuming Kafka data: {e}")
            return {'data': []}  # Return an empty list in case of errors


    # async def get_updated_data(self):






    #     # Fetch updated data from database (like your model)
    #     # data22 = requests.get('http://localhost:5500/data')
        
    

    #     # print(data.text)
    #     # print(type(data.text))
    #     # final = json.loads(data.text)
    #     # data = list(YourModel.objects.values())  # Replace with your model and logic




    #     # # ----------------------------------------------------------------------------------------

    #     """View to consume Kafka data and pass it to the template for display with pagination."""
    #     # user_id = request.GET.get('user_id')  # Retrieve user_id from query params
        
    #     try:
    #         # Initialize Kafka Consumer with Confluent Kafka Consumer
    #         consumer = Consumer({
    #             'bootstrap.servers': ','.join(KAFKA_SERVERS),
    #             'group.id': 'django_consumer_group',
    #             'auto.offset.reset': 'earliest',
    #         })

    #         # Subscribe to the Kafka topic
    #         consumer.subscribe([KAFKA_TOPIC])

    #         data = []
    #         # Consume messages and filter by user_id if provided
    #         try:
    #             # Fetch messages from Kafka
    #             for _ in range(50):  # Fetch a limited number of messages (adjust as needed) my change to -50 to 999
    #                 msg = consumer.poll(timeout=1.0)
    #                 if msg is None:
    #                     continue
    #                 if msg.error():
    #                     if msg.error().code() == KafkaError._PARTITION_EOF:
    #                         continue
    #                     else:
    #                         raise KafkaException(msg.error())
    #                 else:
    #                     # Parse the JSON data received from Kafka
    #                     message_data = json.loads(msg.value().decode('utf-8'))
    #                     # if user_id:  # If user_id is provided, filter the data
    #                     #     if str(message_data.get('USER_ID')) == str(user_id):
    #                     #         data.append(message_data)
                            
    #                     # else:
    #                     #     data.append(message_data)
    #                     data.append(message_data)
            

    #         except KafkaException as e:
    #             print(f"Kafka error: {e}")
    #             return {'data': json.loads(data)}
    #             # return render(request, 'list.html', {'data': [], 'error': str(e)})
            
    #         print(data)

    #         # Close consumer after fetching required records
    #         consumer.close()

    #         # Paginate the data
    #         # paginator = Paginator(data, 10)  # Show 10 messages per page
    #         # page_number = request.GET.get('page')
    #         # page_obj = paginator.get_page(page_number)

    #         return {'data': json.loads(data)}
    #         # return render(request, 'list.html', {'page_obj': page_obj})

    #     except Exception as e:
    #         print(f"Error consuming Kafka data: {e}")
    #         return {'data': json.loads(data)}
    #         # return render(request, 'list.html', {'data': [], 'error': str(e)})
        
    #     # return {'data': json.loads(data22.text)}


















        # ---------------------------------------------------------------------------------------------



















        # return {'data': json.loads(data22.text)}