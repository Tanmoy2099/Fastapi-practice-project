# Application Core Logic (`/core`) 🛡️

This module contains the "Rules" of your application. If you need to change a global password setting, fix an error message, or add a secret API key, you look here.

## How the Core Works

### 1. `config.py` (The Environment Brain)
Hardcoding passwords or database URLs in your code is a massive security risk! If you upload `main.py` with your database password to GitHub, hackers will instantly steal your data.

**The Solution:**
We put all our secrets in a local file called `.env` (which git specifically ignores). 
`config.py` uses `pydantic-settings` to automatically read that `.env` file, extract the secrets (like `mongo_uri`), and load them into a secure, globally available Python object called `settings`. 
Every other file in the app simply imports `settings.mongo_uri` without ever knowing the actual secret!

### 2. `security.py` (The Vault)
This file handles all cryptographic math. 
- **Hash Passwords**: When a user registers, we do NOT save "password123" to the database. We use the `bcrypt` algorithm here to hash it into something unreadable.
- **JWT Tokens**: When a user logs in successfully, we do not give them their password back. We create a JSON Web Token (JWT). This is a base64 string that securely embeds their `user_id` inside it, cryptographically signed by your secret server key. The user uses this JWT keycard to enter locked endpoints. 

### 3. `dependencies.py` (The Bouncer)
In FastAPI, `Depends()` is a magical mechanism. 
Let's say a user wants to view their profile. Before the profile function even starts, FastAPI runs `get_current_active_user`.
This dependency:
1. Looks at the incoming HTTP Request Header for `"Bearer <TOKEN>"`.
2. Takes that Token and throws it into `security.py` to decrypt it.
3. If valid, extracts the `user_id`, opens MongoDB, and finds the exact `User` profile object.
4. Directly injects that `User` object into your endpoint function so you don't even have to write the database query yourself!

### 4. `exceptions.py` & `handlers.py` (The Crash Net)
Imagine a user searches for a post that doesn't exist. Python throws a nasty `Traceback` error.
Instead, we throw a custom `AppException(code="NOT_FOUND")`. 
The handlers in `handlers.py` permanently catch these crashes before they reach the user, gracefully mapping them into a clean JSON response like `{"error": {"code": "NOT_FOUND", "message": "Post not found"}}`.
