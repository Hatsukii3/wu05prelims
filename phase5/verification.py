import pika
import redis
import pymongo

# connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
mongoc = pymongo.MongoClient("localhost:27017")
redisc = redis.Redis(host='localhost', port=6379, password=None, db=0)

#verify mongodb

db = mongoc['prelims']
collection = db['users']

collection.insert_one({"working":True})

#verify redis
redisc.set("hello", "world")

#verify rabbitmq
# channel = connection.channel()
# channel.queue_declare(queue="hello")
# channel.basic_publish(exchange='', routing_key="hello", body="Hello World")


#verify mongodb and redis for now

#print results foreach
print(redisc.get("hello"))
print(collection.find({"working":True})[0])