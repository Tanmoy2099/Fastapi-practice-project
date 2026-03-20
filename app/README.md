# The Application Core (`/app`) 🧠

Welcome to the heart of the backend! If you want to understand how the server boots up, you must understand `app/main.py`.

## What is `main.py`?
`main.py` is the **Entry Point** of your application. Think of it as the motherboard of a computer. It doesn't do all the work itself, but it connects all the different components (RAM, CPU, Hard Drive) together.

When you run `uvicorn app.main:app`, Uvicorn (the web server software) looks exactly here for a variable named `app`.

---

## Breaking Down `main.py` Step-by-Step

Let's look at the exact chronological order of how your app starts.

### 1. The Lifespan (Waking up the Databases)
In modern FastAPI, before the server is allowed to accept a single web request from a user, it runs a special function called **Lifespan Context Manager**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs BEFORE the server starts!
    await connect_db(...)
    await cache.connect()
    yield # SERVER IS NOW AWAKE AND APPS RUN HERE
    # This runs AFTER the server shuts down (Ctrl+C)
    await close_db()
```
**Why is this important?** 
If the app boots up and a user instantly asks for their profile, but MongoDB hasn't finished connecting yet, the app will crash! The lifespan ensures MongoDB and Redis are 100% fully connected *before* it `yields` control to the web server.

### 2. The `app` Instance
```python
app = FastAPI(title=settings.app_name, lifespan=lifespan)
```
This is the holy grail. This creates the actual FastAPI application object. We pass it the title (from our `core/config.py`) and attach the `lifespan` we just talked about.

### 3. Exception Handlers (Catching Crashes)
```python
app.add_exception_handler(AppException, app_exception_handler)
```
Normal Python crashes spit out massive chunks of ugly red text (Tracebacks) and return a `500 Server Error` to the user. We don't want the user seeing our code! 

By adding exception handlers, we tell FastAPI: *"If any code inside the app throws an `AppException`, do NOT crash. Instead, run `app_exception_handler` which will cleanly format the error into a nice JSON response."*

### 4. Middlewares (The Bouncers)
```python
add_security_headers(app)
add_mongo_sanitizer(app)
add_rate_limiter(app)
add_cors(app)
```
Middlewares are pieces of code that intercept a web request *before* it hits your endpoints. 
For example, if a hacker tries to send 1,000 requests a second, the `add_rate_limiter` middleware will catch it and block their IP address before the request even makes it to your routers! *(Read the `/middlewares` README for more info on these).*

### 5. Routing (The Map)
```python
for route in routes:
    app.include_router(**route)
```
Finally, `main.py` imports a massive list of `routes` from your `/api/v1/routes/routes.py` file. It tells the `app` object: *"Here is the map of every URL (like `/api/v1/users`). When a user asks for this URL, send them to that specific Python function!"*

Once this file finishes running from top to bottom, your server is officially online and listening!
