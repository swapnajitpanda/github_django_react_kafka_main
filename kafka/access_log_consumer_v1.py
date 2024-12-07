from confluent_kafka import Consumer, KafkaException
import json
import logging
import threading
import requests

logging.basicConfig(filename='access_logs_consumer.log', level=logging.INFO)

KAFKA_TOPIC = 'iB360_access_logs'
KAFKA_SERVERS = 'localhost:9092'
consumed_messages = []

def consume_messages():
    consumer_config = {
        'bootstrap.servers': KAFKA_SERVERS,
        'group.id': 'iB360_consumer_group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe([KAFKA_TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logging.error(f"Kafka error: {msg.error()}")
                continue
            try:
                record = json.loads(msg.value().decode('utf-8'))
                print('Data: ', record)
                logging.info(f"Consumed message: {record}")
                consumed_messages.append(record)
                # requests.post(http://127.0.0.1:8000/data_list/?format=json,record)  #addon
            except json.JSONDecodeError as e:
                logging.error(f"Message decode error: {e}")
    except Exception as e:
        logging.error(f"Consumer error: {e}")
    finally:
        consumer.close()

consumer_thread = threading.Thread(target=consume_messages, daemon=True)
consumer_thread.start()
