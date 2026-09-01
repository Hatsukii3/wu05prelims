import redis
import pika
import cv2
import numpy as np
import pymongo
import uuid
import time
import os

#setup
imWidth = 640
fileDir = os.path.dirname(os.path.abspath(__file__)) #path of script
ipUrl = 'http://192.168.254.110:8080/video'
enableIP = False #verify ip camera connection
ipCams = dict() #loading camera data
gatheringMode = True # attempt to send 500 image requests in phase 6
gatheringItr = 0

def key(obj):
    return f"{obj['location']}-{obj['network']}-{obj['id']}"

# rabbitmq setup/boilerplate
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672)) #set to port 5673 in jummel's laptop
channel = connection.channel()
channel.queue_declare(queue='requests', durable=False)
channel.queue_declare(queue='timestamps', durable=False) #queue receiving timestamps
print("RabbitMQ Ready")

#redis setup/boilerplate
redisClient = redis.Redis(host='localhost', port=6379, password=None, db=0)
print("Redis Ready")

#mongodb
mdbClient = pymongo.MongoClient("localhost:27017")
mdb = mdbClient["prelims"]
mdbcol = mdb["col1"]
print("MongoDB ready")

#mongodb query to get set of cameras within location & network
mdbdoc = mdbcol.find() #get data for current location
mdbdoc = list(mdbdoc) # to not exhaust results per iteration

print(mdbdoc)
print("MongoDB data fetched")
print("SensingUnit Started...")

# initialize camera status (final)
# ipCams = dict()

for i in mdbdoc:
    redisClient.set(key(i) + "-lock", "no") #set to unlock status
    
    ipCams[key(i)] = cv2.VideoCapture(i["url"], cv2.CAP_FFMPEG, params=[cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10])

    if not ipCams[key(i)].isOpened():
        print(f"Cannot load camera for {key(i)}")

while not (gatheringMode and gatheringItr == 500):
    for i in mdbdoc: #sample amount of cameras
        if(gatheringMode and gatheringItr == 500): #during phase 6, terminate if requests sent is 500
            break
        camID = key(i) #set camera identification
        
        lock_status = redisClient.get(camID + "-lock")
        if(lock_status and lock_status.decode('utf-8') == 'yes'):
            continue

        #timestamp uid
        uid = str(uuid.uuid4())

        channel.basic_publish("", "timestamps", f"stamp1.{uid}.{time.time_ns()}") #record first stamp

        #fetch image (validate with ip camera later)
        capImage = None
        if enableIP:
            capImage = ipCams[camID].read()[1]
        else:
            capImage = cv2.imread(f"{fileDir}/foo1.jpg")

        if capImage is None:
            print(f"Cannot get image for {camID}")
            continue

        #image preprocessing (core)
        capWidth, capHeight, dummy = capImage.shape
        capImage = cv2.cvtColor(capImage, cv2.COLOR_BGR2GRAY) #grayscaling

        encodeParam = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        
        capImage = cv2.resize(src=capImage, dsize=None, fx=(imWidth/min(capWidth, capHeight)), fy=(imWidth/min(capWidth, capHeight)),
                                        interpolation = cv2.INTER_LINEAR) #resizing
        capImage = capImage[0:640, 0:640]
        capJpg = cv2.imencode('.jpeg', capImage, encodeParam)[1] #jpeg compression

        capNpa = np.array(capJpg)
        capBytes = capNpa.tobytes()
     
        #image caching (core)
        print(f"Caching image {camID} of {len(capBytes)/1000} kilobytes")  
        redisClient.set(camID, capBytes)

        #send message to rabbitmq (core)
        print(f"Request to Rabbitmq: {camID}")
        channel.basic_publish("","requests",f"{camID}.{uid}") #camera id alongside request id

        #update lock status (core)
        print(f"Locking: {camID}")
        redisClient.set(camID + "-lock", "yes")

        channel.basic_publish("", "timestamps", f"stamp2.{uid}.{time.time_ns()}") #record second stamp

        # decode and view Image (temporary)
        # decode = np.frombuffer(capBytes, dtype=np.uint8)
        # decode = cv2.imdecode(decode, 0)
        # cv2.imwrite("newimage.jpg", decode)
        # cv2.imshow("IMAGE", decode)
        # k = cv2.waitKey(0)
        # cv2.destroyAllWindows()
        print()
        gatheringItr += 1

#PROGAM SUCCESS!*