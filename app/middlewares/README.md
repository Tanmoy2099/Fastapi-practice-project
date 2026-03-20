# Request Middlewares (`/middlewares`) 🧤

A **Middleware** is a piece of code that stands between the user and your application, acting like an airport security scanner. 

When a user visits `http://your-app.com/api/users`, the request is frozen mid-air globally by this folder. It must pass through every file here *before* the Python Endpoint code is ever allowed to see it!

---

## 🛡️ Breakdown of Operations (The Scanners)

### `cors.py` (Cross-Origin Resource Sharing)
Let's say you build a React website on `http://localhost:3000` that talks to your FastAPI server on `http://localhost:8000`. 
By default, web browsers (like Chrome) will **block** React from talking to FastAPI because they are on different ports (Origin). They think it's a hacker trying to steal data via a malicious website.

This middleware explicitly tells the browser: *"Do not block `localhost:3000`. We trust them. Let them through."* 
We configure exactly who we trust inside `settings.cors_origins`.

### `rate_limiter.py` (The Bouncer)
If a hacker builds a bot to try and guess passwords, they might send 1,000 login requests a second. If they do that, your server's RAM will explode and the website will go offline for everyone (a DDOS attack).

This shield checks the user's IP Address (like a digital License Plate). We tell it: `"100/minute"`. If the user sends 101 requests in 60 seconds, the Bouncer physically blocks the connection. The user receives a `429 Too Many Requests` error and our database is kept perfectly safe.

### `mongo_sanitizer.py` (The Translator)
MongoDB stores data internally as JSON objects. This occasionally creates massive execution vulnerabilities (NoSQL Injection). 
Imagine a hacker sends their password as a JSON command explicitly asking the database to return True: `{"$eq": ""}`. 
This middleware recursively sweeps every single letter of the user's uploaded JSON body. If it sees hazardous NoSQL symbols (like `$where`), it brutally blocks the character, protecting your database from accidentally executing the hacker's command! 

### `security_headers.py` (Helmet)
Your web browser has built-in security features, but you have to actively tell it to turn them on. 
This script forces FastAPI to reply to the user with special invisible HTTP headers. For example, it sends `X-Frame-Options: DENY`. This literally makes it impossible for another website to embed your website inside a hidden `iFrame`, neutralizing "Clickjacking" attacks immediately.
