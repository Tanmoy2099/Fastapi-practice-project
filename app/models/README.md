# Database Models (`/models`) 🗃️

This directory represents the physical structure of your Database. Think of these files as literal Excel Spreadsheets, and the variables inside them as the Columns. 

Because we use **Beanie ODM**, these classes inherit from `beanie.Document`. When you define a class here, Beanie invisibly creates that exact collection inside MongoDB!

---

## The Collections

### `user.py` (The Users Table)
Your standard User profile mapping natively defining columns like `email`, `hashed_password`, and `is_active`. 

**The Graph Trick (`following` array):**
If you want to track who follows who in a standard SQL database (like Postgres), you have to create a massive messy third table. 
In MongoDB, you just create an array inside the `User` document! 
```python
following: list[PydanticObjectId] = []
```
This variable physically embeds a list of ID strings natively inside the user's record. If Tanmoy follows John, John's unique ID is simply appended to Tanmoy's `following` array. Extremely fast, extremely clean. 

### `post.py` (The Content Table)
This defines what a Post looks like. It explicitly mandates every Post must have a `title`, `content`, and an `author_id`. 
The `author_id` is a `PydanticObjectId` (a MongoDB ID string). This is how we link a Post back to the User who wrote it! 

---

## ⚙️ Native Class Methods
These Model classes are not just dumb storage bins! They can actually inherently hold Python Logic functions locally.

For example, look at `.to_response()` inside the models.
When we query the database, it returns the raw document containing things like `hashed_password`. We *never* want to accidentally send standard User objects to the frontend, because the hacker will see the hashed password! 

Calling `await current_user.to_response()` strips the dangerous data out and returns a perfectly safe dictionary right before FastAPI sends it across the internet.
