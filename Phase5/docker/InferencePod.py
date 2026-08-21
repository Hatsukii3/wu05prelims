import pika
import redis
import numpy as np
import cv2
from ultralytics import YOLO
import random
import pickle
import pymongo
import time
import os

# MDB_HOST = os.environ.get("MONGO_HOST", "mongodb.smart-parking")
# REDIS_HOST = os.environ.get("REDIS_HOST", "redis.smart-parking")
# RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq.smart-parking")

MDB_HOST = os.environ.get("MONGO_HOST", "localhost")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")

MDB_PORT = int(os.environ.get("MONGO_PORT", 27017))
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))

# RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5673))


#MongoDB setup
mdbClient = pymongo.MongoClient(f"mongodb://{MDB_HOST}:{MDB_PORT}/")
mdb = mdbClient["prelims"]
mdbcol = mdb["col1"]
print("MongoDB ready")

#RabbitMQ setup
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
channel = connection.channel() #no need to redeclare queue 'requests' and other stamp queues

channel.queue_declare(queue='requests')
channel.queue_declare(queue='timestamps') #queue receiving timestamps

print("RabbitMQ Setup")

    #Redis setup

#redis setup/boilerplate
redisClient = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
print("Redis Ready")

#yolo setup
model = YOLO("model.pt")
print("YOLO Ready")

def getColours(cls_num):
    """Generate unique colors for each class ID"""
    random.seed(cls_num)
    return tuple(random.randint(0, 255) for _ in range(3))


channel.basic_qos(prefetch_count=1)
def consume(ch, method, properties, body):

    print(f"Received {camID}")
    #setup
    count = 0

    #get id
    raw = body.decode("utf-8")
    camID, uid = raw.split(".")

    channel.basic_publish("", "timestamps", f"stamp3.{uid}.{time.time_ns()}") # 3rd tiemstamp
    
    

    #fetch image
    img = redisClient.get(camID)
    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    imgHeight, imgWidth, channels = img.shape

    #fetch polygon
    polygons = redisClient.get(camID+"-polygons") #load from redis
    polygons = pickle.loads(polygons) #convert from bytes to nested list
    inside = [0 for i in range(len(polygons))]
    contours = []


    #image inference
    results = model.track(img, stream=True) 

    for polygon in polygons:
        for vertex in polygon:
            vertex[0] = vertex[0] * imgWidth #convert from percentages to coordinates from scaled images
            vertex[1] = vertex[1] * imgHeight
        contours.append(np.array(polygon, dtype=np.int32))

    # cv2.drawContours(img, contours, -1, (0,255,0), 3)
    
    for result in results:
        class_names = result.names
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center = ((x1+x2)//2,(y1+y2)//2)
            # cv2.circle(img, center,10, (255,0,0))
            for i in range(len(contours)):
                if(cv2.pointPolygonTest(contours[i], center, False) >= 0):
                    inside[i] = 1

    for i in inside:
        if(i == 1):
            count += 1
    print(f"{count} out of {len(contours)} have been detected")

    #update count
    locationID, networkID, cameraID = camID.split("-")
    query = {"location":locationID, "network":networkID, "id": cameraID}
    changes = {"$set": {"count":count}}
    mdbcol.update_one(query, changes)

    
    #update status
    redisClient.set(camID+"-lock","no")


    #manual acknowledgement
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("Packet Received!")
    print()

    channel.basic_publish("", "timestamps", f"stamp4.{uid}.{time.time_ns()}") # 4th tiemstamp


#manual acknowledgement to prevent data loss
print("Inference Program Ready")
channel.basic_consume(queue="requests", on_message_callback=consume)
channel.start_consuming()
print("END")
connection.close()

#SUCCESS!!!