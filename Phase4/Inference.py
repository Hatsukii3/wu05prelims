import pika
import redis
import numpy as np
import cv2
from ultralytics import YOLO
import random
import pickle
import pymongo
<<<<<<< HEAD
import json
=======
>>>>>>> f4e002afa218415de0ec2e959e4a581b4c68d01f
import time

#MongoDB setup
mdbClient = pymongo.MongoClient("mongodb+srv://xandstorm21:xandstorm21@researchprelims.l8nqb3x.mongodb.net/researchprelims.l8nqb3x.mongodb.net")
mdb = mdbClient["prelims"]
mdbcol = mdb["col1"]
print("MongoDB ready")

#RabbitMQ setup
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel() #no need to redeclare queue 'requests' and other stamp queues
channel.queue_declare(queue='requests')
<<<<<<< HEAD
channel.queue_declare(queue='stamp1')
channel.queue_declare(queue='stamp2')
channel.queue_declare(queue="stamp3")
channel.queue_declare(queue="stamp4")
=======
channel.queue_declare(queue='timestamps') #queue receiving timestamps
>>>>>>> f4e002afa218415de0ec2e959e4a581b4c68d01f

print("RabbitMQ Setup")

#Redis setup

#redis setup/boilerplate
redisClient = redis.Redis('localhost', 6379, 0)
print("Redis Ready")

#yolo setup
model = YOLO("yolo11n.pt")
print("YOLO Ready")

def getColours(cls_num):
    """Generate unique colors for each class ID"""
    random.seed(cls_num)
    return tuple(random.randint(0, 255) for _ in range(3))

def consume(ch, method, properties, body):
    #setup
    count = 0

    #get id
    raw = body.decode("utf-8")
    camID, uid = raw.split(".")

<<<<<<< HEAD
    channel.basic_publish("", "stamp3", json.dumps({"uid":uid, "time": time.time_ns()})) 
=======
    channel.basic_publish("", "timestamps", f"stamp3.{uid}.{time.time_ns()}") # 3rd tiemstamp
>>>>>>> f4e002afa218415de0ec2e959e4a581b4c68d01f
    
    print(f"Received {camID}")

    #fetch image
    img = redisClient.get(camID)
    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, 0)
    imgHeight, imgWidth = img.shape

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

    cv2.drawContours(img, contours, -1, (0,255,0), 3)
    
    for result in results:
        class_names = result.names
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center = ((x1+x2)//2,(y1+y2)//2)
            cv2.circle(img, center,10, (255,0,0))
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

    # cv2.imshow("IMAGE", img)
    # k = cv2.waitKey(0)
    # cv2.destroyAllWindows()

    #manual acknowledgement
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("Packet Received!")
    print()
<<<<<<< HEAD
    
    channel.basic_publish("", "stamp4", json.dumps({"uid":uid, "time":time.time_ns()}))

=======

    channel.basic_publish("", "timestamps", f"stamp4.{uid}.{time.time_ns()}") # 4th tiemstamp
>>>>>>> f4e002afa218415de0ec2e959e4a581b4c68d01f


#manual acknowledgement to prevent data loss
print("Inference Program Ready")
channel.basic_consume(queue="requests", on_message_callback=consume)
channel.start_consuming()
print("END")
connection.close()

#SUCCESS!!!