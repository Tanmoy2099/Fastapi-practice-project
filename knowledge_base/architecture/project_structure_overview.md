# Enterprise FastAPI Architecture

This document breaks down the purpose of the core folders existing in your project:

## `app/api/v1/routes/` 🌐
**Concept:** The entry points of the application.
These files contain FastAPI Router decorators (`@router.post`). 
**Enterprise Rule:** Never write business logic here! These should only validate requests (via DTOs), call a Service or Mapper, and return a response.

## `app/core/` 🧠
**Concept:** The non-business infrastructure.
Things like application config (`settings.py`), exception handlers, and security hashing belong here. We also added `base_mapper.py` here because it is a generic system infrastructural interface.

## `app/db/` 💾
**Concept:** Database initialization connections.
Connecting to Mongo, Redis, or Postgres. Note that database *queries* do not belong here, only the connection strings.

## `app/models/` and `app/schemas/` / `app/dto/` 📝
**Concept:** Data shapes.
- `models/` is exclusively for defining Database schemas (e.g., SQLAlchemy or Beanie classes).
- `schemas/` or `dto/` is exclusively for defining Pydantic JSON contracts (what the user sends/receives).

## `app/services/` and `app/repositories/` 🤖
**Concept:** The Business logic layer!
- **Repositories:** Interact with the database. "Get user by ID", "Update Post". This hides SQL/Mongo queries from the rest of the app.
- **Services:** Execute business rules. For example, `CheckoutService` would check user funds, call `PaymentRepository` to deduct balance, and call `EmailService` to send a receipt.

## `app/domain/` 🌍
**Concept:** Pure entity representation.
Sometimes an app needs an internal representation of an entity disconnected from both the HTTP Request (DTO) and the Database framework (Model). The domain holds the purest form of the data structure.
