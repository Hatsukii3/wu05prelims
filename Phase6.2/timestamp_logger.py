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
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost",port=5672))
channel = connection.channel()

#Making sure the queue exists
queue = channel.queue_declare(queue=QUEUE_NAME)
size = queue.method.message_count

print(f"Connected to RabbitMQ.")
print(f"Listening on queue '{QUEUE_NAME}'...\n")

#Callback Function
def callback(ch, method, properties, body):
    data = body.decode("utf-8").split(".")
    stype = data[0]
    uid = data[1]
    timestamp = data[2]

    print(f"UID: {uid} | Time: {timestamp}")

    if uid not in logs:
        logs[uid] = []

    logs[uid].append(timestamp)

    size -= 1

    if(size==0):
        channel.stop_consuming()

#Listens
channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=callback,
    auto_ack=True
)
channel.start_consuming()

#Export to Excel
workbook = Workbook()
sheet = workbook.active
sheet.title = "Timestamp Logs"

# Header row
sheet.append(["UID", "Timestamp"])

# Write timestamps grouped by UID
for uid, timestamps in logs.items():
    for timestamp in timestamps:
        sheet.append([uid, timestamp])

workbook.save(OUTPUT_FILE)

print(f"Spreadsheet saved as '{OUTPUT_FILE}'.")

connection.close()

print("Connection closed.")