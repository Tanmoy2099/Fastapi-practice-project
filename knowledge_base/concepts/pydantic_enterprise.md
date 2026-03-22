# Default Pydantic Masterclass: The Enterprise Guide

Pydantic is the absolute core of FastAPI. It is the engine that converts raw JSON text into perfectly validated Python objects. This guide covers every essential feature a senior engineer uses daily.

---

## 1. The Ellipsis (`...`) & Basic Typing
In Pydantic, the `...` (Ellipsis) strictly means **"This field is absolutely REQUIRED."** There is no default.

```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    # Required. If missing, HTTP 422 error is thrown instantly.
    username: str = ... 
    
    # Has a default fallback. The client does not have to send this!
    country: str = "USA" 
    
    # Optional. The client doesn't have to send this, defaults to None.
    bio: Optional[str] = None 
    # Modern python equivalent: bio: str | None = None
```

---

## 2. Deep Customization using `Field()`
`Field` is Pydantic's Swiss Army Knife. It lets you restrict and mutate data deeply. Use this instead of manually writing `if` statements!

```python
from pydantic import BaseModel, Field

class SecureRegistration(BaseModel):
    # Enforce lengths and Regex patterns. 
    # If the user sends "Aa", the API automatically rejects them.
    username: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")
    
    # Mathematical restraints: ge = greater or equal, lt = strictly less than
    age: int = Field(..., ge=18, lt=100) 
    
    # Hide internal fields! "exclude=True" means this variable is NEVER 
    # accidentally serialized into an outgoing JSON response.
    hashed_password: str = Field(..., exclude=True)

    # Automatically generate timestamps using a default_factory!
    from datetime import datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 3. Data Transformers (Custom Validators)
Sometimes data is technically the right type, but messy. We use `@field_validator` to clean or strictly reject it.

### Before Mode (Cleaning Data)
Run code *before* Pydantic validates the type. Great for stripping whitespace or coercing weird string dates.
```python
from pydantic import BaseModel, field_validator

class UserProfile(BaseModel):
    email: str

    @field_validator('email', mode='before')
    @classmethod
    def clean_email(cls, v: str) -> str:
        # User types "   John@TEST.com  " -> we fix it instantly to "john@test.com"
        return v.strip().lower()
```

### After Mode (Business Rules)
Run code *after* Pydantic verifies it's a string.
```python
class PasswordSet(BaseModel):
    password: str

    @field_validator('password')
    @classmethod
    def enforce_strong_rules(cls, v: str) -> str:
        if "!" not in v and "@" not in v:
            raise ValueError("Password is too weak. Must contain ! or @")
        return v
```

### Model Validators (Cross-Field Checks)
Need to compare two different fields? Use `@model_validator(mode='after')`!
```python
from pydantic import model_validator

class Meeting(BaseModel):
    start_time: int
    end_time: int

    @model_validator(mode='after')
    def check_times(self) -> 'Meeting':
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after Start time!")
        return self
```

---

## 4. Computed Fields (`@computed_field`)
Sometimes you want your API to automatically return a field that the user never posted, calculated on the fly.
```python
from pydantic import BaseModel, computed_field

class Person(BaseModel):
    first_name: str
    last_name: str

    @computed_field
    @property
    def full_name(self) -> str:
        # Every time model_dump() is called, this is automatically appended to the JSON!
        return f"{self.first_name} {self.last_name}"
```

---

## 5. Aliases (Mapping CamelCase to Snake_Case)
Front-end developers write JS in `camelCase` (e.g. `firstName`). Back-end Python engineers write `snake_case` (e.g. `first_name`). Aliases auto-translate them seamlessly.

```python
from pydantic import BaseModel, Field, ConfigDict

# Fast One-off Alias:
class SingleAlias(BaseModel):
    # Frontend sends {"first_name": "Tom"} but we access it via model.first_name
    first_name: str = Field(..., alias="firstName") 

# Enterprise Global Alias Config:
def to_camel(string: str) -> str:
    # Basic logic to convert snake to camel...
    parts = iter(string.split('_'))
    return next(parts) + ''.join(word.title() for word in parts)

class GlobalAliasModel(BaseModel):
    # We write snake_case normally!
    first_name: str 
    last_name: str
    
    # Pydantic automatically converts every single field using `alias_generator`
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True # Allows creating the model via Model(first_name="Tom") OR Model(firstName="Tom")
    )
```

---

## 6. Advanced Polymorphism (`discriminator`)
When an endpoint accepts multiple completely different shapes of data (like a Card payment OR a Crypto payment), enterprise apps use Discriminated Unions for ultra-fast validation without messy `if/else` checks.

```python
from pydantic import BaseModel, Field
from typing import Literal, Union

# "Literal" means that field MUST perfectly match the string inside it.
class Card(BaseModel):
    type: Literal["card"]
    card_number: str

class Crypto(BaseModel):
    type: Literal["crypto"]
    wallet_address: str

class PaymentProcessor(BaseModel):
    # Pydantic looks precisely at the "type" key to instantly validate the correct model structure!
    method: Union[Card, Crypto] = Field(..., discriminator="type")
```

---

## 7. Extracting DB Models safely (`from_attributes`)
When you select data using SQLAlchemy, you get an ORM Database Object, NOT a JSON dictionary. Pydantic can safely read object attributes (`db_user.name` instead of `db_user['name']`).

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    name: str

    # This critical flag tells Pydantic: "It's safe to read from a Class object instead of typical JSON dictionary!"
    model_config = ConfigDict(from_attributes=True)

# Usage:
# db_user_record = session.query(User).first()
# return UserResponse.model_validate(db_user_record)
```

---

## 8. Managing Enterprise `.env` Variables (`pydantic-settings`)
Never manually use `os.getenv()`. Pydantic strictly validates your `.env` file upon boot. If your Staging server forgets to define a `DATABASE_URL`, Pydantic forces the app to crash hard immediately, which saves hours of debugging later.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_environment: str = "PRODUCTION"
    database_url: str # NO DEFAULT. If the .env is missing this, the app crashes!
    redis_port: int = 6379 # It will automatically cast the .env string to an Int!
    
    class Config:
        env_file = ".env"

# Validate upon execution:
config = Settings()
```

---
**Summary:** If you master `Field()`, Validators (`@field_validator`), Discriminated Unions (`Union[..., discriminator]`), and `model_config`, you will be writing Pydantic exactly like senior Staff Engineers at top-tier SaaS companies.
