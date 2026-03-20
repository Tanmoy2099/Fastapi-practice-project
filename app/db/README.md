# Databases (`/db`) 🗄️

This directory is responsible for turning the electricity on for your databases. 

## `mongo.py`
This script connects to the physical MongoDB database using the standard asynchronous `Motor` driver. However, we do not interact directly with raw PyMongo dictionaries. That is slow and confusing!

### The Magic of Beanie ODM
Instead, we use an Object-Document Mapper (ODM) called **Beanie**. 
In `mongo.py`, we call `init_beanie`. We hand it a list of our Python classes (like `User` and `Post` found in the `/models` folder). 
Beanie instantly analyzes those classes, builds exact database indexes, and allows us to query MongoDB natively using Python!

**Example without Beanie (Ugly):**
```python
db.users.find_one({"_id": ObjectId("123")})
```

**Example with Beanie (Beautiful & Safe):**
```python
await User.find_one(User.id == "123")
```

To understand how our memory-cache database boots up, deeply explore `app/db/redis/README.md`!
