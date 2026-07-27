import json
import pika
from openpyxl import Workbook

#Configuration var
QUEUE_NAME = "timestamps"
OUTPUT_FILE = "DATA.xlsx"

#Storage
#Dictionary to group timestamps by Correlation ID
logs = {}

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

#Making sure the queue exists
queue = channel.queue_declare(queue=QUEUE_NAME)
size = queue.method.message_count
print(f"Amount of messages: {size}")

print(f"Connected to RabbitMQ.")
print(f"Listening on queue '{QUEUE_NAME}'...\n")

#Callback Function
def callback(ch, method, properties, body):
    global size
    data = body.decode("utf-8").split('.')
    print(data)
    uid = data[1]
    stype = data[0]
    timestamp = data[2]

    print(f"UID: {uid} | Time: {timestamp}")

    if uid not in logs:
        logs[uid] = {"stamp1":0, "stamp2":0, "stamp3":0, "stamp4":0}

    logs[uid][stype] = int(timestamp)

    size -= 1

    if(size==0):
        channel.stop_consuming()

#Listens
channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=callback,
    auto_ack=True
)

if(size != 0):  
    channel.start_consuming()

#Export to Excel
workbook = Workbook()
sheet = workbook.active
sheet.title = "Timestamp Logs"

# Header row
sheet.append(["Gathering", "Lifetime", "Inference"])

# Write timestamps grouped by UID
for uid, timestamps in logs.items():
    #print values in miliseconds
    sheet.append([
        (timestamps["stamp2"]-timestamps["stamp1"])/1000000,
        (timestamps["stamp3"]-timestamps["stamp2"])/1000000,
        (timestamps["stamp4"]-timestamps["stamp3"])/1000000])

workbook.save(OUTPUT_FILE)

print(f"Spreadsheet saved as '{OUTPUT_FILE}'.")

connection.close()

print("Connection closed.")