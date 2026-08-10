import json 
import pika
from openpyxl import Workbook

# Configuration Variables
QUEUE_NAME = "timestamps"
OUTPUT_FILE = "data3.xlsx"

# Storage
logs = {}                  

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', port=5673))
channel = connection.channel()

# Making sure the queue exists
queue = channel.queue_declare(queue=QUEUE_NAME)
size = queue.method.message_count
print(f"Amount of messages: {size}")

print("Connected to RabbitMQ")
print(f"Listening on queue '{QUEUE_NAME}'...\n")

# Callback Function 
def callback(ch, method, properties, body):
    global size
    data = body.decode('utf-8').split(".")
    
    stype = data[0]
    uid = data[1]
    timestamp = data[2]

    print(f"UID: {uid} | Type: {stype} | Timestamp: {timestamp}")

    if uid not in logs:
        logs[uid] = {"stamp1":0, "stamp2":0, "stamp3":0, "stamp4":0}

    logs[uid][stype] = int(timestamp)

    size -= 1

    if (size == 0):
        channel.stop_consuming()

# Listens
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

if (size > 0):
    channel.start_consuming()

# Export to Excel
workbook = Workbook()
sheet = workbook.active
sheet.title = "Timestamp logs"

# Write Timestamps 
for uid, timestamps, in logs.items():
    # Prints sheet values
    sheet.append([
        (timestamps["stamp2"]-timestamps["stamp1"])/1000000,
        (timestamps["stamp3"]-timestamps["stamp2"])/1000000,
        (timestamps["stamp4"]-timestamps["stamp3"])/1000000
    ])

#column 1: latency sensing unit program
#column 2: queue lifetime
#column 3: latency inference program

workbook.save(OUTPUT_FILE)

print(f"Spreadsheet saved as '{OUTPUT_FILE}'.")

connection.close()

print("Connection closed")