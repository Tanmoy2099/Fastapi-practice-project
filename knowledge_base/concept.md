# Enterprise Pydantic: Concepts & Deep Dive

This file covers the **Concepts** behind FastAPI's most critical library: Pydantic.

## 🤔 Why do we need Pydantic?
When data comes across the internet (via JSON), it is essentially just raw text. Your Python application needs that text to become safe, strictly-typed Python objects (like integers, booleans, and datetime classes). 

Pydantic does all of this parsing and validation automatically using standard Python type hints.

---

## 🏢 Enterprise-Level Use Cases & Implementation

In a professional enterprise context, Pydantic is used for these 4 primary concepts:

### 1. API Payload Validation (DTOs)
* **Concept:** If a user sends a string instead of an int, the API automatically rejects it with an exact HTTP 422 error detailing the exact field. No internal crashes!
```python
from pydantic import BaseModel, Field, EmailStr

class UserSignUpDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr # Validates email strings natively!
    age: int = Field(..., ge=18) # ge = greater than or equal to 18
```

### 2. Environment Variable Configuration (`BaseSettings`)
* **Concept:** Pydantic `BaseSettings` automatically reads `.env` variables and validates them upon boot!
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My Enterprise App"
    database_url: str

    class Config:
        env_file = ".env"

# If DB_URL is missing in .env, the app instantly crashes on boot. This is enterprise safety!
settings = Settings()
```

### 3. ORM Mapping (SQLAlchemy to Pydantic)
* **Concept:** When pulling data from an SQL database, Pydantic safely converts the DB Object to a JSON-ready Python Pydantic Model via `from_attributes`.
```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    username: str
    
    model_config = ConfigDict(from_attributes=True) 

# Usage inside a FastAPI Route
# db_user = get_user_from_database()
# return UserResponse.model_validate(db_user)
```

### 4. Advanced Polymorphism (Discriminated Unions)
* **Concept:** When a request can be one of multiple shapes (e.g., Payment can be Card or PayPal). Instead of 1 giant model with lots of optional fields, enterprise apps use Discriminated Unions.
```python
from pydantic import BaseModel, Field
from typing import Literal, Union

class CardPayment(BaseModel):
    type: Literal["card"]
    card_number: str

class PaypalPayment(BaseModel):
    type: Literal["paypal"]
    token: str

class PaymentRequest(BaseModel):
    payment: Union[CardPayment, PaypalPayment] = Field(..., discriminator="type")
```
