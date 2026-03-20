# The Redis Caching Engine (`/redis`) ⚡

While MongoDB is the massive hard drive storing millions of rows of permanent data, **Redis** is your ultra-fast, volatile computer RAM. 

Querying a hard drive (Mongo) takes milliseconds. Querying RAM (Redis) takes microseconds. We use Redis anytime we need extreme speed or temporary storage.

### `core.py` (The Foundation)
This file houses the base `CacheStore` object class. During application boot up, it uses `aioredis` to build an invisible network bridge directly to your Redis container. It natively outlines exactly how to `.set()`, `.get()`, and `.delete()` specific keys directly in memory. 

### `token_store.py` (Digital Keycards)
Tokens are highly sensitive and require immediate remote destruction abilities. 
When a user visits `/login`, the server generates a JWT Refresh string. We force that token directly into the `token_store.py` class cache. 
- **The Problem**: JWTs cannot be "deleted". They expire mathematically on the clock. So how do you "logout" a user early?
- **The Solution (Redis)**: When they click "Logout", we find their Token inside Redis and physically delete the key. The next time they try to use that Token, the server asks Redis if the token is valid. Redis returns `None`, and the server rejects them instantly!

### `permission_store.py` (Cutting Wait Times)
Let's say to load a page, you need to know if a User is an "Admin" or a "Standard" user. If you ask MongoDB for this 1,000 times a second, your server will melt.
Instead, the first time you ask Mongo, you save the answer into the `permission_store.py` (Redis). For the next 999 requests, FastAPI skips Mongo completely and grabs the answer out of Redis in a fraction of a millisecond!
