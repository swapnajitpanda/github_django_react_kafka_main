from confluent_kafka import Producer
import cx_Oracle
import logging
import json
from datetime import datetime

logging.basicConfig(filename='access_logs_producer.log', level=logging.INFO)

KAFKA_TOPIC = 'iB360_access_logs'
KAFKA_SERVERS = ['localhost:9092']
ORACLE_DB_CONFIG = {
    'user': 'shreyash',
    'password': 'shreyash',
    'dsn': 'orcl-aws.c8sefhobaih4.ap-south-1.rds.amazonaws.com:1521/ORCL',
}

def handle_datetime(data):
    if isinstance(data, datetime):
        return data.isoformat()
    if isinstance(data, dict):
        return {k: handle_datetime(v) for k, v in data.items()}
    if isinstance(data, list):
        return [handle_datetime(item) for item in data]
    return data

def get_kafka_producer():
    try:
        producer = Producer({'bootstrap.servers': ','.join(KAFKA_SERVERS)})
        logging.info("Kafka producer initialized.")
        return producer
    except Exception as e:
        logging.error(f"Producer initialization error: {e}")
        raise

def fetch_oracle_data(query):
    try:
        connection = cx_Oracle.connect(**ORACLE_DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return rows
    except cx_Oracle.Error as e:
        logging.error(f"Oracle error: {e}")
        raise

def send_to_kafka(producer, data):
    if not data:
        logging.warning("No data to send.")
        return
    for record in data:
        sanitized = handle_datetime(record)
        producer.produce(KAFKA_TOPIC, json.dumps(sanitized))
    producer.flush()
