# Pydantic Schemas (`/schemas`) 📏

This folder is probably the most powerful feature of FastAPI. 

**Models** (`/models`) describe what data looks like *inside* your database.
**Schemas** (`/schemas`) describe what data must look like when traveling *across the internet*.

We use a library called **Pydantic** to build these validation templates. 

---

## 🚫 Why Do We Need Schemas?

Imagine you have a Registration endpoint that accepts a brand new user.
If you don't have validation, a hacker could send this JSON to your server:
```json
{
    "email": "not_an_email",
    "password": "123",
    "is_admin": True
}
```
If you blindly save this to MongoDB, your app will crash because the email is fake, the password is too short, and the user just successfully made themselves an Admin!

---

## ✅ The Pydantic Solution

Instead, we force incoming JSON to pass through a Schema like `UserCreate`:

```python
class UserCreate(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: str
```
By telling FastAPI to use this `UserCreate` schema, Pydantic acts as an impenetrable wall. 

If the user uploads the bad JSON from earlier, Pydantic literally blocks the request and screams back a `422 Unprocessable Entity` error automatically. It explicitly tells the user: *"Hey, 'not_an_email' is not a valid email format, and 'is_admin' is not an allowed field here."*

### Clean Documentation
Another massive benefit: Because FastAPI knows exactly what your `BaseModel` classes look like, it automatically generates a beautiful Website Interface (Swagger UI at `/docs`) that shows frontend developers exactly what JSON they are allowed to send to you!
