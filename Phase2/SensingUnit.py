import redis
import pika
import cv2
import numpy as np
import pymongo

#setup
locationID = "Location1"
networkID = "pferrero_5G"
imWidth = 640
ipUrl = 'http://192.168.254.110:8080/video'

def key(cameraID):
    return f"{locationID}-{networkID}-{cameraID}"

# rabbitmq setup/boilerplate
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='requests')
print("RabbitMQ Ready")

#redis setup/boilerplate
redisClient = redis.Redis('localhost', 6379, 0)
print("Redis Ready")

#mongodb
mdbClient = pymongo.MongoClient("mongodb+srv://xandstorm21:xandstorm21@researchprelims.l8nqb3x.mongodb.net/researchprelims.l8nqb3x.mongodb.net")
mdb = mdbClient["prelims"]
mdbcol = mdb["col1"]
print("MongoDB ready")

#mongodb query to get set of cameras within location & network
mdbdoc = mdbcol.find({"location": locationID, "network": networkID}) #get data for current location
mdbdoc = list(mdbdoc) # to not exhaust results per iteration

print("MongoDB data fetched")
print("SensingUnit Started...")

# initialize camera status (final)
ipCams = dict()

for i in mdbdoc:
    redisClient.set(key(i["id"]) + "-lock", "no") #set to unlock status
    print("foo")
    ipCams[key(i["id"])] = cv2.VideoCapture(i["url"])
    print("bar")

while True:
    for i in mdbdoc: #sample amount of cameras
        uid = key(i['id']) #set camera identification
        if(redisClient.get(uid + "-lock") == b'yes'):
            continue
        #fetch image (validate with ip camera later)
        capImage = ipCams[uid].read()[1]

        #image preprocessing (core)
        capWidth, capHeight, dummy = capImage.shape
        capImage = cv2.cvtColor(capImage, cv2.COLOR_BGR2GRAY) #grayscaling

        encodeParam = [int(cv2.IMWRITE_JPEG_QUALITY), 10]
        capImage = cv2.resize(src=capImage, dsize=None, fx=(imWidth/max(capWidth, capHeight)), fy=(imWidth/max(capWidth, capHeight)),
                              interpolation = cv2.INTER_LINEAR) #resizing
        capJpg = cv2.imencode('.jpeg', capImage, encodeParam)[1] #jpeg compression
        capNpa = np.array(capJpg)
        capBytes = capNpa.tobytes()
     
        #image caching (core)
        print(f"Caching image {uid} of {len(capBytes)/1000} kilobytes")  
        redisClient.set(uid, capBytes)

        #send message to rabbitmq (core)
        print(f"Request to Rabbitmq: {uid}")
        channel.basic_publish("","requests",uid)

        #update lock status (core)
        print(f"Locking: {uid}")
        redisClient.set(uid + "-lock", "yes")

        # decode and view Image (temporary)
        decode = np.frombuffer(capBytes, dtype=np.uint8)
        decode = cv2.imdecode(decode, 0)
        cv2.imshow("IMAGE", decode)
        k = cv2.waitKey(0)
        cv2.destroyAllWindows()

#PROGAM SUCCESS!