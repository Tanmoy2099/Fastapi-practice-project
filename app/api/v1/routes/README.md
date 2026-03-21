# Core Endpoint Logic (`/routes`) 🚦

If `/v1` is the umbrella, the `/routes` folder is the actual engine! 

Every Python file inside this directory represents a completely different feature of your backend. For example, `auth.py` handles User Login/Registration, while `posts.py` handles creating and fetching content feeds. 

Let's dive into exactly how the code in this directory works.

---

## 🏎️ The Auto-Discovery Engine (`routes.py`)

If you look at the `main.py` file, you'll see this line:
```python
for route in routes:
    app.include_router(**route)
```
Wait, how does `main.py` know that `auth.py`, `users.py`, and `posts.py` exist? Did you manually import them one by one? 

**No!** That is the genius of `routes.py`. It explicitly avoids you having to manually write an import every single time you create a new endpoint file.

### How `routes.py` works step-by-step:
1. It uses Python's `Path` library to look at its own folder (`/routes/`) and finds every single file ending in `.py`.
2. It loops over these files. It specifically skips itself (`routes.py`) and `__init__.py`. 
3. For every file it finds (like `auth.py`), it uses Python's `importlib` to physically open the file in memory. 
4. It checks: *"Does this file have a variable called `router`?"* (Because in `auth.py`, you create `router = APIRouter()`).
5. If it does, it grabs that `router` object and jams it into a massive Python list. `main.py` takes that list and securely maps all those URLs to the internet!

**TL;DR:** If you want to create a new feature (like `payments.py`), just drop it in this folder! Make sure it has a `router = APIRouter()` variable, and it will be *automatically* connected to the internet. 

---

## 🔒 Endpoints Breakdown: What the code actually does

The files in this folder are **"Thin Routers"**. They do NOT contain complex business rules or database queries. Their only job is to understand the HTTP Request, hand the data to the **Service Layer** (`app/services`), and return the response.

### 1. The Gateway: `auth.py`
This file serves your endpoints for authentication.
- **Registration (`/register`) & Login (`/login`)**: 
  These endpoints take the JSON payload, validate it via Pydantic, and immediately hand the email and password to `auth_service.py`. The service handles hashing and generates the tokens. The route's only job when the service returns the tokens is to securely format the HTTP Response by setting the `HttpOnly` Refresh Token cookie.
- **Logout (`/logout-all`)**: 
  Delegates to the service to permanently blacklist tokens in Redis, and commands the client's browser to execute `response.delete_cookie()`.

### 2. The People: `users.py`
This file exposes the social graph endpoints.
- **Profile Queries (`/me`)**: 
  Uses the FastAPI Dependency `Depends(get_current_active_user)` to magically intercept the Authorization token, decrypt it, and inject the Python `User` object into the request.
- **Follow System (`/users/{id}/follow`)**: 
  Extracts the target user ID and passes it straight to `user_service.follow(current_user, target_id)`. The service handles all the logic of checking if you already follow them.

### 3. The Content: `posts.py`
This file handles content creation and consumption.
- **CRUD (Create, Read, Update, Delete)**: 
  Endpoints like `POST /posts/` strictly require `current_active_user`, locking strangers out. The incoming JSON is passed directly to `post_service.create(...)`.
- **The Engine (`/feed`)**:
  When you ask for your Feed, the route calls `post_service.get_feed(current_user)`. The route itself has no idea how the feed is assembled, whether it comes from Redis cache, or how the MongoDB aggregation pipelines run. By keeping this logic out of the route, the route remains extremely fast and easy to test!
