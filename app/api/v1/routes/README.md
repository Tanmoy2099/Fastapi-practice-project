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

### 1. The Gateway: `auth.py`
This file is heavily guarded. It controls who is allowed into your application.
- **Registration (`/register`)**: 
  When you POST JSON here, the code extracts your `body.password` plaintext string. It immediately passes it through `security.get_password_hash`. This transforms "my_password" into an ugly, unreadable 60-character scrambled string using Bcrypt. Only this scrambled string is saved into the MongoDB Database using `.insert()`. 
- **Login (`/login`)**: 
  Takes your email and looks you up in MongoDB natively (`await User.find_one()`). If you exist, it checks if the password matches the scrambled hash. If yes, it creates an encrypted string called a JSON Web Token (JWT). It saves your unique "Refresh" token securely into the **Redis Database** natively so it can remember you.
- **Logout (`/logout-all`)**: 
  Instantly tells Redis to permanently delete every trace of your authorization keys. Your current token dies immediately.

### 2. The People: `users.py`
This file handles actions a user takes against *another* user's profile.
- **Profile Queries (`/me`)**: 
  Have you noticed that `/me` doesn't require an `id` in the URL? That's because it uses a FastAPI `Depends(get_current_active_user)`. This Dependency magically intercepts your Authorization token, decrypts it, finds out who you are, looks you up in Mongo, and directly injects your Python object right into the `current_user` variable!
- **Follow System**: 
  When you hit `/users/123/follow`, the code queries MongoDB. It finds your `User` profile object, grabs the `following` list (which is an array of IDs), and natively appends `123` to that array and updates MongoDB (`await current_user.save()`).

### 3. The Content: `posts.py`
This file handles content creation securely.
- **CRUD (Create, Read, Update, Delete)**: 
  The `/posts` endpoints universally require `current_active_user`, locking strangers out entirely. When creating a post, it forces the author to be your exact ID natively.
- **The Engine (`/feed`)**:
  This is the brilliant part. When you ask for your Feed, the code does not search all posts in the database. 
  Instead, it grabs your `following` array containing the exact IDs of the people you follow. It invokes MongoDB's massive `In(...)` operator natively searching for *only* posts where the `author_id` intersects your explicit target array list. It perfectly filters the data without crashing Python's memory!
