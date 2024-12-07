
# # # # check============================================
# from django.shortcuts import render
# from django.http import HttpResponse

# def trigger_producer(request):
#     # Your producer logic goes here
#     return HttpResponse("Producer Triggered!")





# from django.shortcuts import render
# from django.http import JsonResponse
# from confluent_kafka import Consumer, KafkaException, KafkaError
# import json
# import logging

# from .access_logs_producer_v2 import get_kafka_producer, fetch_oracle_data, send_to_kafka

# # Kafka Configuration
# KAFKA_TOPIC = 'iB360_access_logs'
# KAFKA_SERVERS = ['localhost:9092']

# logger = logging.getLogger(__name__)

# def kafka_data_view(request):
#     """View to consume Kafka data and pass it to the template for display with pagination."""
#     try:
#         # Initialize Kafka Consumer with Confluent Kafka Consumer
#         consumer = Consumer({
#             'bootstrap.servers': ','.join(KAFKA_SERVERS),  # Set Kafka broker(s)
#             'group.id': 'django_consumer_group',  # Consumer group ID
#             'auto.offset.reset': 'earliest',  # Start from the earliest message if no offset
#         })

#         # Subscribe to the Kafka topic
#         consumer.subscribe([KAFKA_TOPIC])

#         data = []
#         # Consume messages
#         try:
#             # Fetch 10 messages from the Kafka topic
#             for _ in range(10):
#                 msg = consumer.poll(timeout=1.0)  # Adjust timeout as needed
#                 if msg is None:
#                     continue  # No message
#                 if msg.error():
#                     if msg.error().code() == KafkaError._PARTITION_EOF:
#                         # End of partition
#                         continue
#                     else:
#                         raise KafkaException(msg.error())
#                 else:
#                     # Parse the JSON data received from Kafka
#                     message_data = json.loads(msg.value().decode('utf-8'))
#                     data.append(message_data)  # Append parsed data

#         except KafkaException as e:
#             logger.error(f"Kafka error: {e}")
#             return render(request, 'list.html', {'data': [], 'error': str(e)})

#         # Close consumer after fetching required records
#         consumer.close()
#         print(data)

#         # Pass the parsed data to the template
#         return render(request, 'list.html', {'data': data})

#     except Exception as e:
#         logger.error(f"Error consuming Kafka data: {e}")
#         return render(request, 'list.html', {'data': [], 'error': str(e)})
    
# # check====================================================================================================================
# # addon---.......................................................................................................
# correct---------------------------------------------------------------------------------------------------------------------------

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import logging
from .access_logs_producer_v2 import get_kafka_producer, fetch_oracle_data, send_to_kafka

# Kafka Configuration
KAFKA_TOPIC = 'iB360_access_logs'
KAFKA_SERVERS = ['localhost:9092']

logger = logging.getLogger(__name__)

def trigger_producer(request):
    print('----------------------------Trigger is Activated--------------------')
    """View to trigger the Kafka producer."""
    try:
        # Initialize the producer
        producer = get_kafka_producer()

        # Fetch data from MySQL (or Oracle, as per your logic)
        # query = """SELECT * FROM user_activity ORDER BY ID DESC"""  # Adjust the query if needed
        query = """SELECT * FROM user_activity ORDER BY ID DESC"""  # Adjust the query as needed
        data = fetch_oracle_data(query)

        # Send data to Kafka
        send_to_kafka(producer, data)

        # return HttpResponse(f'{"status"  "success"  "message" "Data sent to Kafka successfully."}')
        return HttpResponse(f'"status" : "success" , "message": "Data sent to Kafka successfully." <br> <a href="/data/web/"> Go to Page </a>')
    except Exception as e:
        logger.error(f"Error in producer view: {e}")
        return HttpResponse({"status": "error", "message": str(e)})


def kafka_data_view(request):
    """View to consume Kafka data and pass it to the template for display with pagination."""
    user_id = request.GET.get('user_id')  # Retrieve user_id from query params
    
    try:
        # Initialize Kafka Consumer with Confluent Kafka Consumer
        consumer = Consumer({
            'bootstrap.servers': ','.join(KAFKA_SERVERS),
            'group.id': 'django_consumer_group',
            'auto.offset.reset': 'earliest',
        })

        # Subscribe to the Kafka topic
        consumer.subscribe([KAFKA_TOPIC])

        data = []
        # Consume messages and filter by user_id if provided
        try:
            # Fetch messages from Kafka
            for _ in range(50):  # Fetch a limited number of messages (adjust as needed) my change to -50 to 999
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())
                else:
                    # Parse the JSON data received from Kafka
                    message_data = json.loads(msg.value().decode('utf-8'))
                    if user_id:  # If user_id is provided, filter the data
                        if str(message_data.get('USER_ID')) == str(user_id):
                            data.append(message_data)
                    else:
                        data.append(message_data)

        except KafkaException as e:
            logger.error(f"Kafka error: {e}")
            return render(request, 'list.html', {'data': [], 'error': str(e)})

        # Close consumer after fetching required records
        consumer.close()

        # Paginate the data
        paginator = Paginator(data, 10)  # Show 10 messages per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'list.html', {'page_obj': page_obj})

    except Exception as e:
        logger.error(f"Error consuming Kafka data: {e}")
        return render(request, 'list.html', {'data': [], 'error': str(e)})
    
def home(request):
    return render(request, 'home.html')


def kafka_user_data_api(request):
    """
    API to fetch Kafka messages filtered by user_id.
    """
    user_id = request.GET.get('user_id')  # Retrieve user_id from query params

    if not user_id:
        return JsonResponse({"status": "error", "message": "user_id is required"}, status=400)

    try:
        # Initialize Kafka Consumer
        consumer = Consumer({
            'bootstrap.servers': ','.join(KAFKA_SERVERS),
            'group.id': 'user_data_group',
            'auto.offset.reset': 'earliest',
        })
        
        consumer.subscribe([KAFKA_TOPIC])

        filtered_data = []
        for _ in range(50):  # Fetch up to 50 messages   if error comes i have to chnage it to 999
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            else:
                record = json.loads(msg.value().decode('utf-8'))
                if str(record.get('USER_ID')) == str(user_id):
                    filtered_data.append(record)

        consumer.close()

        if not filtered_data:
            return JsonResponse({"status": "success", "message": "No records found for the provided user_id"}, status=200)

        return JsonResponse({"status": "success", "data": filtered_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
# correct---------------------------------------------------------------------------------------------------------------------------


# from django.shortcuts import render
# from django.http import JsonResponse
# from django.core.paginator import Paginator
# from confluent_kafka import Consumer, KafkaException, KafkaError
# import json
# import logging

# logger = logging.getLogger(__name__)

# KAFKA_TOPIC = 'iB360_access_logs'
# KAFKA_SERVERS = ['localhost:9092']

# def kafka_data_view(request):
#     """View to consume Kafka data and pass it to the template with pagination and filtering."""
#     user_id = request.GET.get('user_id')  # Retrieve user_id from query params
#     data = []

#     try:
#         # Initialize Kafka Consumer with Confluent Kafka Consumer
#         consumer = Consumer({
#             'bootstrap.servers': ','.join(KAFKA_SERVERS),
#             'group.id': 'django_consumer_group',
#             'auto.offset.reset': 'earliest',
#         })

#         consumer.subscribe([KAFKA_TOPIC])

#         # Consume messages
#         try:
#             for _ in range(100):  # Fetch up to 100 messages
#                 msg = consumer.poll(timeout=1.0)
#                 if msg is None:
#                     continue
#                 if msg.error():
#                     if msg.error().code() == KafkaError._PARTITION_EOF:
#                         continue
#                     else:
#                         raise KafkaException(msg.error())
#                 else:
#                     message_data = json.loads(msg.value().decode('utf-8'))
#                     # If user_id filter is applied, only append matching records
#                     if user_id:
#                         if str(message_data.get('USER_ID')) == str(user_id):
#                             data.append(message_data)
#                     else:
#                         data.append(message_data)

#         except KafkaException as e:
#             logger.error(f"Kafka error: {e}")
#             return render(request, 'list.html', {'data': [], 'error': str(e)})

#         consumer.close()

# #         # Paginate data (10 records per page)
#         paginator = Paginator(data, 10)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)

#         return render(request, 'list.html', {'data': page_obj, 'page_obj': page_obj, 'user_id': user_id})

#     except Exception as e:
#         logger.error(f"Error consuming Kafka data: {e}")
#         return render(request, 'list.html', {'data': [], 'error': str(e)})












# from django.shortcuts import render
# from django.http import JsonResponse
# from django.core.paginator import Paginator
# from confluent_kafka import Consumer, KafkaException, KafkaError
# import json
# import logging

# logger = logging.getLogger(__name__)

# KAFKA_TOPIC = 'iB360_access_logs'
# KAFKA_SERVERS = ['localhost:9092']

# def kafka_data_view(request):
#     """View to consume Kafka data and pass it to the template with pagination and filtering."""
#     user_id = request.GET.get('user_id')  # Retrieve user_id from query params
#     data = []

#     try:
#         # Initialize Kafka Consumer with Confluent Kafka Consumer
#         consumer = Consumer({
#             'bootstrap.servers': ','.join(KAFKA_SERVERS),
#             'group.id': 'django_consumer_group',
#             'auto.offset.reset': 'earliest',
#         })

#         consumer.subscribe([KAFKA_TOPIC])

#         # Consume messages
#         try:
#             for _ in range(100):  # Fetch up to 100 messages
#                 msg = consumer.poll(timeout=1.0)
#                 if msg is None:
#                     continue
#                 if msg.error():
#                     if msg.error().code() == KafkaError._PARTITION_EOF:
#                         continue
#                     else:
#                         raise KafkaException(msg.error())
#                 else:
#                     message_data = json.loads(msg.value().decode('utf-8'))
#                     # If user_id filter is applied, only append matching records
#                     if user_id:
#                         if str(message_data.get('USER_ID')) == str(user_id):
#                             data.append(message_data)
#                     else:
#                         data.append(message_data)

#         except KafkaException as e:
#             logger.error(f"Kafka error: {e}")
#             return render(request, 'list.html', {'data': [], 'error': str(e)})

#         consumer.close()

#         # Sort the data in decreasing order (most recent first)
#         data.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

#         # Paginate data (10 records per page)
#         paginator = Paginator(data, 10)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)

#         return render(request, 'list.html', {'data': page_obj, 'page_obj': page_obj, 'user_id': user_id})

#     except Exception as e:
#         logger.error(f"Error consuming Kafka data: {e}")
#         return render(request, 'list.html', {'data': [], 'error': str(e)})
# # kafka/views.py
# from django.shortcuts import render

# def home(request):
#     return render(request, 'home.html')



# # # kafka/views.py
# from django.shortcuts import render

# def data_view(request):
#     # Example data
#     data = {'message': 'Hello, world!'}
#     return render(request, 'data_view.html', data)




























# from django.shortcuts import render
# from django.http import JsonResponse
# from django.core.paginator import Paginator
# from confluent_kafka import Consumer, Producer, KafkaException
# import json
# import logging

# # Global Logger
# logger = logging.getLogger(__name__)

# # Kafka Configuration
# KAFKA_TOPIC = 'iB360_access_logs'
# KAFKA_SERVERS = 'localhost:9092'  # Replace with your Confluent Kafka broker(s)
# GROUP_ID = 'django_consumer_group'

# # Kafka Producer Configuration (if needed)
# PRODUCER_CONFIG = {
#     'bootstrap.servers': KAFKA_SERVERS
# }

# # Kafka Consumer Configuration
# CONSUMER_CONFIG = {
#     'bootstrap.servers': 'localhost:9092',
#     'group.id': 'django_consumer_group',
#     'auto.offset.reset': 'earliest',
# }


# def kafka_data_view(request):
#     """
#     Render paginated Kafka data for a specific user_id.
#     """
#     user_id = request.GET.get('user_id')  # Get user_id from query parameters

#     # Consume data from Kafka
#     try:
#         consumer = Consumer(CONSUMER_CONFIG)
#         consumer.subscribe([KAFKA_TOPIC])
        
#         data = []
#         while True:
#             msg = consumer.poll(timeout=1.0)  # Poll for messages
#             if msg is None:
#                 break  # No more messages
#             if msg.error():
#                 if msg.error().code() == KafkaException._PARTITION_EOF:
#                     break
#                 else:
#                     raise KafkaException(msg.error())
#             message = json.loads(msg.value().decode('utf-8'))
#             data.append(message)

#         consumer.close()

#     except Exception as e:
#         logger.error(f"Error consuming Kafka data: {e}")
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#     # Filter data by user_id
#     if user_id:
#         filtered_data = [record for record in data if str(record.get('USER_ID')) == str(user_id)]
#     else:
#         filtered_data = data  # Show all data if user_id is not provided

#     # Pagination
#     paginator = Paginator(filtered_data, 10)  # Show 10 records per page
#     page_number = request.GET.get('page', 1)  # Get current page number
#     page_obj = paginator.get_page(page_number)

#     return render(
#         request,
#         'list.html',
#         {'page_obj': page_obj, 'user_id': user_id}
#     )


# def kafka_data_api(request):
#     """
#     API view to fetch data from Kafka and return as JSON.
#     """
#     try:
#         consumer = Consumer(CONSUMER_CONFIG)
#         consumer.subscribe([KAFKA_TOPIC])

#         data = []
#         while True:
#             msg = consumer.poll(timeout=1.0)
#             if msg is None:
#                 break
#             if msg.error():
#                 if msg.error().code() == KafkaException._PARTITION_EOF:
#                     break
#                 else:
#                     raise KafkaException(msg.error())
#             message = json.loads(msg.value().decode('utf-8'))
#             data.append(message)
#             if len(data) >= 10:  # Limit to 10 records
#                 break

#         consumer.close()

#         return JsonResponse({'status': 'success', 'data': data}, safe=False)

#     except Exception as e:
#         logger.error(f"Error fetching Kafka data: {e}")
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# def trigger_producer(request):
#     """
#     View to trigger the Confluent Kafka producer.
#     """
#     try:
#         producer = Producer(PRODUCER_CONFIG)

#         def delivery_report(err, msg):
#             if err is not None:
#                 logger.error(f"Message delivery failed: {err}")
#             else:
#                 logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

#         # Example data to send
#         data = {"USER_ID": 123, "ACTION": "LOGIN", "TIMESTAMP": "2024-12-04T10:00:00Z"}
#         producer.produce(
#             KAFKA_TOPIC,
#             key=str(data["USER_ID"]),
#             value=json.dumps(data),
#             callback=delivery_report
#         )

#         producer.flush()  # Wait for all messages to be delivered
#         return JsonResponse({"status": "success", "message": "Message sent to Kafka successfully."})

#     except Exception as e:
#         logger.error(f"Error producing Kafka message: {e}")
#         return JsonResponse({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------------------------------

