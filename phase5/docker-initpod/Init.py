import os
import pickle
import pymongo
import redis

MDB_HOST = os.environ.get("MONGO_HOST", "mongodb.smart-parking")
MDB_PORT = int(os.environ.get("MONGO_PORT", 27017))

REDIS_HOST = os.environ.get("REDIS_HOST", "redis.smart-parking")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# Setup MongoDB
mdbClient = pymongo.MongoClient(f"mongodb://{MDB_HOST}:{MDB_PORT}/")
db = mdbClient["prelims"]
collection = db["col1"]
collection.drop()

mdb_init_data = [
    {
        "location": "Location1",
        "network": "pferrero_5G",
        "id": "1",  
        "url": "http://192.168.254.110:8080/video",
        "max_count": 2,
        "count": 0,
    }
]

collection.insert_many(mdb_init_data)
print("MongoDB data inserted!")

# Setup Redis
redisClient = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
print("Redis Ready")

# Generation of polygons since there is no phase 1
maxheight = 640
maxwidth = 427

# Creation of 2 polygons, one occupied and one vacant spot
sample_coords = [
    [[62, 368], [117, 366], [126, 452], [71, 456]],
    [[107, 232], [155, 230], [159, 289], [107, 289]],
]

# Convert to coordinate ratios
for i in sample_coords:
    for j in i:
        j[0] = j[0] / maxwidth
        j[1] = j[1] / maxheight

print(sample_coords)
data = pickle.dumps(sample_coords)

# Link to redis
redisClient.set("Location1-pferrero_5G-1-polygons", data)
print("SUCCESS!")

#hardcode data before testing