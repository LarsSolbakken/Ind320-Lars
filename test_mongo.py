from pymongo import MongoClient

# Use the URI string from Atlas (this goes inside Python, not terminal)
uri = "mongodb+srv://tveit001_db_user:Am5spYHS69kraxQF@cluster0.3m91rus.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)

db = client["ind320_db"]
collection = db["test_collection"]

collection.insert_one({"id": 1, "name": "Alice"})
collection.insert_one({"id": 2, "name": "Bob"})

for doc in collection.find():
    print(doc)

