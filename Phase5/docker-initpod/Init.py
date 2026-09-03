import pickle
import redis
import pymongo


#setup mongodb
mdbClient = pymongo.MongoClient("localhost:27017")
db = mdbClient['prelims']
collection = db['col1']
collection.drop()

sample_coords = [[[611, 231], [639, 228], [639, 272], [610, 271]], [[611, 276], [610, 304], [638, 308], [635, 271]], [[579, 269], [606, 266], [606, 307], [582, 312]], [[580, 236], [614, 238], [610, 266], [583, 267]], [[550, 235], [582, 238], [579, 270], [545, 267]], [[544, 270], [574, 274], [572, 313], [547, 310]], [[518, 237], [547, 240], [544, 271], [512, 269]], [[485, 241], [524, 239], [513, 269], [482, 269]], [[455, 238], [482, 236], [477, 270], [449, 265]], [[419, 238], [450, 234], [446, 272], [413, 268]], [[388, 243], [410, 243], [411, 271], [380, 266]], [[369, 274], [396, 284], [391, 323], [365, 313]], [[405, 271], [437, 273], [428, 321], [409, 321]], [[446, 274], [469, 277], [465, 317], [434, 315]], [[485, 271], [513, 276], [499, 317], [470, 313]], [[513, 272], [539, 268], [539, 328], [511, 323]]]
data_template = {
    "location":"Location1",
    "network":"pferrero_5G",
    "id": 1,
    "url": "http://192.168.254.110:8080/video",
    "max_count": len(sample_coords),
    "count": 0
}

#to enable scalin
mdb_init_data = []

cameraAmt = 56 #this is for the number of camera loads 

for i in range(cameraAmt):
    data = data_template.copy()
    data["id"] = str(i + 1)
    mdb_init_data.append(data)

collection.insert_many(mdb_init_data)
print("MongoDB data inserted!")

#setup redis
redisClient = redis.Redis('localhost', 6379, 0)
print("Redis Ready")

#generation of polygons since there is no phase 1

maxheight = 640
maxwidth = 640



#convert to coordinate 
for i in sample_coords:
    for j in i:
        j[0] = j[0]/maxwidth
        j[1] = j[1]/maxheight 

print(sample_coords)
data = pickle.dumps(sample_coords)

for i in range(len(mdb_init_data)):
    redisClient.set(f"Location1-pferrero_5G-{i+1}-polygons", data) #link to redis

print("SUCCESS!")