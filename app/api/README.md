# API Framework (`/api`) 🌐

This module acts as the organized file cabinet for all of your URL endpoints. 

When a Frontend Developer (like a React or mobile app developer) wants to communicate with your backend, they don't care about your database or your Python functions. They only care about hitting specific URLs (like `GET http://your-website.com/api/v1/users`).

This folder exists strictly to organize those URLs.

### Why not put URLs in `main.py`?
If you build an app like Twitter, you will eventually have hundreds of URLs (login, logout, post tweet, delete tweet, like tweet, block user, etc.). If you put all 1,000 lines of code into `main.py`, your code will become a massive, unreadable nightmare. 

This `/api` folder acts as an umbrella, splitting our endpoints into smaller, organized folders based exclusively on **Versioning**.

Next stop: read the `README.md` inside `/api/v1/` to learn why Versioning is critical!
