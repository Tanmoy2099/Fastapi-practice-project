# Enterprise FastAPI Architecture 

This file explains the overarching **Architecture** design of your application.
The goal of architecture is **Separation of Concerns**: ensuring the API layer doesn't know about the Database layer.

### Directory Layout & Rules

#### `app/api/v1/routes/` 🌐
**Concept:** The entry points of the application.
**Enterprise Rule:** Never write business logic here! These should only validate requests (via DTO schemas), call a Service or Mapper, and return a response.

#### `app/core/` 🧠
**Concept:** The non-business infrastructure.
Things like application config (`settings.py`), custom exception handlers, JWT utilities, or `base_mapper.py` belong here. 

#### `app/db/` 💾
**Concept:** Database connection initialization.
Connecting to Mongo, Redis, or Postgres databases. Note that database *queries* do not belong here, only the connection code.

#### `app/models/` and `app/schemas/` (or `dto/`) 📝
**Concept:** Data shapes.
- `models/` is exclusively for defining Database records (e.g., SQLAlchemy or Beanie classes).
- `schemas/` or `dto/` is exclusively for defining Pydantic JSON contracts (what the API accepts/returns).

#### `app/services/` and `app/repositories/` 🤖
**Concept:** The Business logic layer!
- **Repositories:** Interact with the database. "Get user by ID", "Update Post". This hides SQL/Mongo queries from the rest of the app!
- **Services:** Execute business rules independent of the database. For example, `CheckoutService` checks user funds, calls `PaymentRepository` to deduct balance, and calls `EmailService` to send a receipt.

#### `app/domain/` 🌍
**Concept:** Pure business entities.
When an app needs an internal representation of an entity disconnected from both the HTTP Request (DTO) and the Database framework (Model), we create a pure class here. We map to this layer via `mappers/`.
