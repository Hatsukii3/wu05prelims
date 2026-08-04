import pickle
import redis
import pymongo


#setup mongodb
mdbClient = pymongo.MongoClient("localhost:27017")
db = mdbClient['prelims']
collection = db['col1']
collection.drop()

mdb_init_data = [
    {
        "location":"Location1",
        "network":"pferrero_5G",
        "id": 1,
        "url": "http://192.168.254.110:8080/video",
        "max_count": 2,
        "count": 0
    }
]

collection.insert_many(mdb_init_data)
print("MongoDB data inserted!")

#setup redis
redisClient = redis.Redis('localhost', 6379, 0)
print("Redis Ready")

#generation of polygons since there is no phase 1

maxheight = 640
maxwidth = 427

#creation of 2 polygons, one occupied and one vacant spot
sample_coords = [
    [[62, 368],[117, 366],[126, 452],[71, 456]],
    [[107, 232],[155, 230], [159, 289], [107, 289]]
]

#convert to coordinate 
for i in sample_coords:
    for j in i:
        j[0] = j[0]/maxwidth
        j[1] = j[1]/maxheight 

print(sample_coords)
data = pickle.dumps(sample_coords)
redisClient.set(f"Location1-pferrero_5G-1-polygons", data) #link to redis
print("SUCCESS!")