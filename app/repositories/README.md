# The Repository Layer (`/repositories`) 🗄️

Welcome to the **Data Access Layer**. 

Every single database query (MongoDB/Beanie) the application runs is securely isolated inside this folder. **No other folder in the application is allowed to import a database Model and run a query!**

---

## 🏗️ Why do we need a Repository layer?

When managing business logic, you never want your rules permanently glued to a specific database technology.

```text
HTTP Request -> Route -> Service -> REPOSITORY -> Database
```

**The Benefits:**
1. **Database Agnosticism**: The `Service` layer asks the repository: `"Get me the user by email"`. It doesn't know *how* the repository fetches that data. If we migrate from MongoDB to PostgreSQL tomorrow, we **only** rewrite the files in this folder. The `Service` and `Route` files remain 100% untouched!
2. **Centralized Queries**: If you need to optimize a slow database query, you know precisely where to find it.

---

## 📂 The Repositories

### 1. `user_repo.py`
Encapsulates all `User` object retrieval and persistence. 
- Fast standard Beanie lookups: `.find_one()`, `.get()`, `.insert()`.
- Social Graph queries: Finding lists of followers and the users you are following.

### 2. `post_repo.py`
Contains the complex logic needed to assemble content feeds. This repository is special because it natively drops down into **PyMongo** to write raw Aggregation Pipelines, bypassing the Beanie ODM for extreme performance.

---

## 🚀 Deep Dive: Aggregation Pipelines (`get_feed`)

When assembling the Feed, we do not retrieve every post and filter it in Python (which would consume massive RAM). Instead, we build an **Aggregation Pipeline**.
Think of this as writing raw `SELECT ... WHERE ... ORDER BY` in SQL. It instructs the database hardware to filter and sort the data natively before handing it to Python.

Inside `post_repo.py`, the pipeline natively maps like this:

```python
pipeline = [
    # STAGE 1 ($match): SQL 'WHERE'
    # The physical database filters out anything where the author_id 
    # is NOT in your following list. Python never even sees the discarded posts.
    {"$match": {"author_id": {"$in": current_user.following}, "published": True}},
    
    # STAGE 2 ($sort): SQL 'ORDER BY DESC'
    # Sorts surviving data chronologically right on the hard drive
    {"$sort": {"created_at": -1}}
]

# Execute native PyMongo Aggregation (Extremely Fast)
cursor = Post.get_pymongo_collection().aggregate(pipeline)
return await cursor.to_list(length=None)
```

By keeping this highly-specialized PyMongo code absolutely locked inside `post_repo.py`, the rest of the application remains clean, generic, and unbothered by complex database syntax!
