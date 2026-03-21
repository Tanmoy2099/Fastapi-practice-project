# The Service Layer (`/services`) 🧠

Welcome to the **Brain** of the application!

The files in this directory contain all of the **Business Logic**. If you want to know *how* the application behaves (e.g. what happens when a user follows someone, or how the cache is updated when a post is created), this is exactly where you look.

---

## 🏗️ Why do we need a Service layer?

In simple tutorials, developers usually put all their logic straight into the FastAPI HTTP routes (`app/api/v1/routes/`). 
However, in a professional production environment, we enforce a **Clean Architecture**.

```text
HTTP Request -> Route -> SERVICE -> Repository -> Database
```

We decouple the "What the app does" (Service) from "How the app connects to the internet" (Route).

**The Benefits:**
1. **Reusability**: If we want to add a GraphQL API tomorrow, the GraphQL resolvers just import `auth_service.py`! We don't have to rewrite any login logic. We could even build a Command Line Interface (CLI) that creates users by calling `userService.create(...)`.
2. **Readability**: The HTTP `routes` files are incredibly thin and purely handle Network logic (JSON parsing, Cookies, Headers). The complex `if/else` rules reside cleanly here.
3. **Testability**: Service functions can be unit-tested efficiently using Mock Repositories, entirely independent of HTTP or raw Databases.

---

## 📂 The Services

### 1. `auth_service.py`
Handles all authentication logic:
- Prevents duplicate emails/usernames during registration.
- Uses `core/security.py` to encrypt/decrypt passwords via Bcrypt.
- Generates Access (JWT) and Refresh Tokens.
- Orchestrates the `token_store` (Redis) to validate and revoke refresh sessions.

### 2. `user_service.py`
Manages the Social Graph (Following/Unfollowing):
- Enforces rules: *"A user cannot follow themselves"* and *"You cannot follow a user you are already following"*.
- Delegates to the `user_repo` to permanently persist these relationships to MongoDB.

### 3. `post_service.py`
Handles Content Caching and Feed Assembly:
- **Authorization**: Ensures that a user is not allowed to update or delete a post unless they own it, or they are an Admin.
- **Caching**: Aggressively leverages Redis to cache the Feed. When a user creates a new post (`create`), it automatically invalidates their Feed cache so the new post appears immediately!
