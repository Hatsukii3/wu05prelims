import pika
import redis
import numpy as np
import cv2
from ultralytics import YOLO
import random
import pickle
import pymongo
import torch

# MongoDB Setup

mdbClient = pymongo.MongoClient(
    "mongodb+srv://xandstorm21:xandstorm21@researchprelims.l8nqb3x.mongodb.net/researchprelims.l8nqb3x.mongodb.net"
)

mdb = mdbClient["prelims"]
mdbcol = mdb["col1"]

print("MongoDB Ready")

# RabbitMQ Setup

connection = pika.BlockingConnection(
    pika.ConnectionParameters("rabbitmq")
)

channel = connection.channel()

# Create queue if it doesn't exist
channel.queue_declare(queue="requests", durable=True)

print("RabbitMQ Ready")

# Redis Setup

redisClient = redis.Redis("redis",6379,0)


print("Redis Ready")

# Use Nano model (fastest)
model = YOLO("yolo11n.pt")

print("YOLO Ready")

def getColours(cls_num):
    random.seed(cls_num)
    return tuple(random.randint(0,255) for _ in range(3))

def consume(ch, method, properties, body):

    count = 0

    uid = body.decode()

    print(f"Processing {uid}")

    img = redisClient.get(uid)

    if img is None:
        print("Image not found")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    img = np.frombuffer(img,dtype=np.uint8)

    img = cv2.imdecode(img,cv2.IMREAD_GRAYSCALE)

    img = cv2.resize(img,(640,640))

    imgHeight,imgWidth = img.shape


    polygons = redisClient.get(uid+"-polygons")

    polygons = pickle.loads(polygons)

    inside = [0]*len(polygons)

    contours = []

    for polygon in polygons:

        scaled=[]

        for x,y in polygon:

            scaled.append([
                int(x*imgWidth),
                int(y*imgHeight)
            ])

        contours.append(
            np.array(scaled,dtype=np.int32)
        )

    with torch.inference_mode():

        results = model.predict(

            img,

            classes=[2,5,7],      # car bus truck

            verbose=False

        )

    for result in results:

        for box in result.boxes:

            x1,y1,x2,y2 = map(int,box.xyxy[0])

            center=((x1+x2)//2,(y1+y2)//2)

            for i in range(len(contours)):

                if cv2.pointPolygonTest(

                    contours[i],

                    center,

                    False

                )>=0:

                    inside[i]=1

    count=sum(inside)

    print(f"{count}/{len(contours)} occupied")

    locationID,networkID,cameraID=uid.split("-")

    query={

        "location":locationID,

        "network":networkID,

        "id":cameraID

    }

    changes={

        "$set":{

            "count":count

        }

    }

    mdbcol.update_one(query,changes)

    redisClient.set(uid+"-lock","no")

    ch.basic_ack(

        delivery_tag=method.delivery_tag

    )

    print("Done\n")


print("Inference Program Ready")

channel.basic_qos(prefetch_count=1)

channel.basic_consume(

    queue="requests",

    on_message_callback=consume

)

channel.start_consuming()

connection.close()