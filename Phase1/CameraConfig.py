print("NOTE: PLEASE DON'T INPUT FIELDS WITH THE CHARACTER \"-\"")

import redis
import pika
import cv2
import numpy as np
import pymongo
import os
import pickle

#setup
location = "Location1"
ssid = ""
fileDir = os.path.dirname(os.path.abspath(__file__)) #path of script
imWidth = 640  #fixed width after taking bufferImage
bufferPolygon = [] # mapping spot
bufferPolygons = [] # stored mapping spots
bufferContours = [] # contour states with bufferPolygons
bufferImage = None # for global access of temporary image
bufferImageCopy = None # to clear window for editing spot events
enableIP = False # either real ip cameras or use sample bufferImage
quitSpotMaking = False # check if user quits editing parking spots
deletedPolygon = False # check if user deletes a polygon


#mongodb
mdbClient = pymongo.MongoClient("localhost:27017")
mdb = mdbClient["prelims"]
mdbcol = mdb["col1"]
print("MongoDB ready")

#redis
redisClient = redis.Redis(host="localhost", port="6379")
print("Redis Ready")

#load data

data = None



def updateData():
    print("Refetching mongodb")
    global data
    data = [i for i in mdbcol.find()]

updateData()

def createNewObject():
    while True:
        exitInput = True
        newLocationName = input("Location Name: ")
        newSSIDName = input("SSID: ")
        newCameraID = input("Camera ID: ")

        for i in data:
            if(newLocationName == i['location'] and newSSIDName == i['network'] and newCameraID == i['id']):
                exitInput = False

        if(exitInput): break
        else:
            print("Object already exists with the same details.")


    newCameraURL = input("HTTP/RTSP url: ")
    

    newObject = {
        "location": newLocationName,
        "network": newSSIDName,
        "count":0,
        "url": newCameraURL,
        "max_count":0,
        "id": newCameraID
    }

    mdbcol.insert_one(newObject)
    updateData()
    configureObject(newObject)

def editObject():

    locationQuery = []
    ssidQuery = []

    print("Results #1")
    for i in data:
        print(f"{i["location"]}-{i["network"]}-{i["id"]}")

    newLocationName = input("Location Name: ")

    print("\nResults #2")
    

    for i in data:
        if(i["location"] == newLocationName):
            print(f"{i["location"]}-{i["network"]}-{i["id"]}")
            locationQuery.append(i)

    newSSIDName = input("SSID: ")

    for i in locationQuery:
        if(i["network"] == newSSIDName):
            print(f"{i["location"]}-{i["network"]}-{i["id"]}")
            ssidQuery.append(i)


    newCameraID = input("Camera ID: ")

    selectedObj = None

    for i in ssidQuery:
        if(i['id'] == newCameraID):
            selectedObj = i

    if(selectedObj == None):
        print("Error: Object does not exist based on the 3 given parameters")
        return

    configureObject(selectedObj)

def configureObject(obj): #new set of prompts after selecting/creating object
    print(f"Configuring: {obj['location']}-{obj['network']}-{obj['id']}")

    while True:
        print()
        print("(1) Edit RTSP/HTTP URL")
        print("(2) Edit Parking spots")
        print("(3) Exit")

        choice = input("Enter Choice: ")

        if(choice == "1"): #update url
            newURL = input("Enter New URL")
            mdbcol.find_one_and_update({
                "location": obj['location'],
                'id':obj['id'],
                'network':obj['network']
            },{
                "$set": {"url":newURL}
            })
            updateData()
        elif(choice == "2"):
            configureSpots(obj)
        elif (choice == "3"):
            break
        else:
            print("Please Enter a Valid Input")

def configureSpots(obj):
    global bufferPolygons, quitSpotMaking, bufferContours, bufferImage, bufferImageCopy


    bufferImage = cv2.imread(f"{fileDir}/foo.jpeg")
    

    capWidth, capHeight, dummy = bufferImage.shape
    bufferImage = cv2.resize(src=bufferImage, dsize=None, fx=(imWidth/max(capWidth, capHeight)), fy=(imWidth/max(capWidth, capHeight)),
                                      interpolation = cv2.INTER_LINEAR) #resizing
    capHeight, capWidth,  dummy = bufferImage.shape #update sizes

    bufferImageCopy = bufferImage.copy() #get copy to clear window properly 

    bytePolygons = redisClient.get(f"{obj['location']}-{obj['network']}-{obj['id']}-polygons")

    if(bytePolygons == None):
        bufferPolygons = []
    else:
        bufferPolygons = pickle.loads(bytePolygons)
    
    bufferContours = []
    #covert back from percentages to pixels
    for i in bufferPolygons:
        for j in i:
            j[0] = int( j[0] * capWidth)
            j[1] = int( j[1] * capHeight)
        bufferContours.append(np.array(i, dtype=np.int32))

  
    print(type(bufferPolygons))

    
    quitSpotMaking = False

    print("RIGHT CLICK (DELETE POLYGON) | LEFT CLICK (MARK VERTICES)")

    while not quitSpotMaking:
        markSpot()
        bufferImage = bufferImageCopy.copy()


    #parse into percentages and store to redis
    for i in bufferPolygons:
        for j in i:
            j[0] /= capWidth
            j[1] /= capHeight

    #update polygons
    redisClient.set(f"{obj['location']}-{obj['network']}-{obj['id']}-polygons", pickle.dumps(bufferPolygons))

    #update max vehicle count
    mdbcol.find_one_and_update({
        "location":obj['location'],
        "id": obj['id'],
        "network": obj['network'],
    }, {
        "$set": {"max_count":len(bufferPolygons)} #amount of polygons
    })

    updateData()
 #refer to this    


    


def spotMouseEvent(event, x, y, flags, param):
    global deletedPolygon, bufferPolygons, bufferContours
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked coordinates: X={x}, Y={y}")
        # Modify the bufferImage passed through the 'param' argument
        cv2.circle(param['bufferImage'], (x, y), 5, (255, 0, 0), 1)
        bufferPolygon.append([x,y])

    if event == cv2.EVENT_RBUTTONDOWN:
        for i in range(len(bufferContours)):
            if(cv2.pointPolygonTest(bufferContours[i], (x,y), False) >= 0):
                deletedPolygon = True
                del bufferContours[i]
                del bufferPolygons[i]
                break



def markSpot():
    global bufferPolygon, deletedPolygon, quitSpotMaking

    cv2.polylines(bufferImage, np.array(bufferPolygons), True, (255,0,0,100), 3)

    for i in range(len(bufferPolygons)):
        ax = 0;
        ay = 0;
        for j in range(len(bufferPolygons[i])):
            ax += bufferPolygons[i][j][0]
            ay += bufferPolygons[i][j][1]

        
        text = str(i+1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2        

        (tw,th),baseline = cv2.getTextSize(text, font, font_scale, thickness)

        ax = (ax//4) - (tw//2)
        ay = (ay//4) +  (th//2)
        

        cv2.putText(bufferImage, text, (ax, ay), font, font_scale, (0,255,0), 1)                                

    cv2.namedWindow("Add Parking Spot")
    cv2.setMouseCallback("Add Parking Spot", spotMouseEvent, param={
        "bufferImage":bufferImage
    })

    while True:
        cv2.imshow("Add Parking Spot", bufferImage)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            quitSpotMaking = True
            break

        if deletedPolygon:
            deletedPolygon = False
            break

        if len(bufferPolygon) == 4:
            bufferPolygons.append(bufferPolygon)
            bufferContours.append(np.array(bufferPolygon, dtype=np.int32))
            break

    bufferPolygon = []
    cv2.destroyAllWindows()
    print(bufferPolygons)


#next tasks
#create main prompt properly making choice either choosing to edit or create new object

while True:
    print("YELLOW")
    print("(1) Edit Camera Object")
    print("(2) Create Camera Object")
    print("(3) Exit")

    choice = input("Enter choice: ")

    if(choice == "1"):
        editObject()
    elif(choice == "2"):
        createNewObject()
    elif(choice == "3"):
        break
    else:
        print("Please enter a valid input. ")