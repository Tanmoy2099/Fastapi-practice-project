# API Versioning (`/api/v1`) 🛤️

Welcome to Version 1! 

As a beginner, you might wonder: *"Why do we need a `/v1` folder? Why not just put the routes directly in `/api`?"*

### The Problem of Breaking Changes
Imagine you build a wildly successful mobile app. A million users download the app onto their iPhones. Right now, your iPhone app specifically expects the URL `GET /api/users` to return a user's first name like this:
```json
{"first_name": "Tanmoy"}
```

A year goes by. You decide you want to combine first and last names. You rewrite your Python backend so it now returns:
```json
{"full_name": "Tanmoy"}
```
**DISASTER!** Every single person who hasn't updated their iPhone app will experience a massive crash. Their app is still looking for `"first_name"`, but the server is now returning `"full_name"`. 

### The Solution: API Versioning
To prevent this, professional backends put all their URLs inside a `/v1` shell:
`GET /api/v1/users`

When you decide to rewrite the underlying structure a year later, you **do not touch `/v1`**. Instead, you create a brand new folder called `/v2`. 
- The older iPhones keep working perfectly because they are still hitting `/v1`.
- iPhones that download the new update will start hitting `/v2`.

You will see exactly where the actual endpoint logic lives inside the `/routes` folder next!
