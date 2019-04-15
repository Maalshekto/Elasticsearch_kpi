import json
import psycopg2
from kafka import KafkaConsumer

consumer = KafkaConsumer("metrics", bootstrap_servers=['172.22.0.3:9092'], group_id="metrics")

try:
    connection = psycopg2.connect(user="postgres",
                                  password="azerty",
                                  host="172.22.0.30",
                                  port="5432",
                                  database="postgres")



    for message in consumer:
        record = json.loads(message.value.decode())
        message = record.get("message", "KO")
        value = record.get("value", 0)
        name = record.get("name", "unknown")
        cluster_name = record.get("cluster_name", "unknown")
        timestamp = record.get("timestamp", 0)
        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO metrics (message, value, name, cluster_name, timestamp) VALUES (%s,%s,%s,%s, to_timestamp(%s))"""
        record_to_insert = (message, value, name, cluster_name, timestamp)
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()
        count = cursor.rowcount
        print ("*", end="", flush=True)

except (Exception, psycopg2.Error) as error :
    if(connection):
        print("Failed to insert record into mobile table", error)
finally:
    #closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
