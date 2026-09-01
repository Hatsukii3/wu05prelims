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
fileDir = os.path.dirname(os.path.abspath(__file__)) #path of script
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
model = YOLO(f"{fileDir}/best.pt")
print("YOLO Ready")

def getColours(cls_num):
    """Generate unique colors for each class ID"""
    random.seed(cls_num)
    return tuple(random.randint(0, 255) for _ in range(3))


channel.basic_qos(prefetch_count=1)
def consume(ch, method, properties, body):

    #setup
    count = 0

    #get id
    raw = body.decode("utf-8")
    camID, uid = raw.split(".")
    print(f"Received {camID}")
    channel.basic_publish("", "timestamps", f"stamp3.{uid}.{time.time_ns()}") # 3rd tiemstamp
    
    

    #fetch image
    img = redisClient.get(camID)
    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    img = img.astype(np.uint8)
    imgWidth, imgHeight, channels = img.shape

    #fetch polygon
    print(camID)
    polygons = redisClient.get(camID+"-polygons") #load from redis
    polygons = pickle.loads(polygons) #convert from bytes to nested list
    inside = [0 for i in range(len(polygons))]
    contours = []


    #image inference
    results = model.predict(source=img) 

    for polygon in polygons:
        for vertex in polygon:
            vertex[0] = vertex[0] * imgWidth #convert from percentages to coordinates from scaled images
            vertex[1] = vertex[1] * imgHeight
        contours.append(np.array(polygon, dtype=np.int32))

    cv2.drawContours(img, contours, -1, (0,255,0), 3)
    
    for result in results:
        class_names = result.names
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center = ((x1+x2)//2,(y1+y2)//2)
            cls = int(box.cls[0])
            class_name = class_names[cls]
            if(class_name == "space-occupied"):
                cv2.rectangle(img, (x1, y1), (x2, y2), (255,0,0), 2)
                cv2.circle(img, center,3, (255,0,0))
                for i in range(len(contours)):
                    if(cv2.pointPolygonTest(contours[i], center, False) > 0):
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

    # decode = np.frombuffer(capBytes, dtype=np.uint8)
    # decode = cv2.imdecode(decode, 0)
    cv2.imshow("IMAGE", img)
    k = cv2.waitKey(0)
    cv2.destroyAllWindows()


#manual acknowledgement to prevent data loss
print("Inference Program Ready")
channel.basic_consume(queue="requests", on_message_callback=consume)
channel.start_consuming()
print("END")
connection.close()

#SUCCESS!!!