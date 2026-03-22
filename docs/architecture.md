# Clean Architecture Guide (Domain-DTO-Mapper Pattern)

Welcome! If you are reading this, you are likely a new member of the team or looking to understand how we structure our features in this project. 

We use a **Domain-DTO-Mapper layered architecture**. This might sound complex, but it essentially means we separate **what the API receives/sends** from **the actual core business logic**.

---

## 🏗 The 3 Core Pillars

### 1. DTO (Data Transfer Objects) 
**Folder:** `app/dto/`
* **What are they?** Pydantic schemas that ONLY handle incoming API requests and outgoing API responses. 
* **Why do we need them?** We want to validate what the user sends us via HTTP. API contracts change frequently; by keeping DTOs separate, changing an API endpoint structure doesn't break our core app logic.
* **Example:** `OrderRequest` ensures the user sends the right JSON payload, enforcing things like required fields or polymorphic payment methods (Card vs PayPal).

### 2. Domain Models
**Folder:** `app/domain/`
* **What are they?** Pure Python objects (often Pydantic or Dataclasses) that represent our actual business entities (e.g., An `Order`, a `User`, a `Payment`).
* **Why do we need them?** These are free from API rules and Database configurations. They represent the single source of truth for our business logic.

### 3. Mappers
**Folder:** `app/mappers/` & `app/core/base_mapper.py`
* **What are they?** Utility classes responsible for translating a **DTO** into a **Domain Model** (and vice-versa). 
* **Why do we need them?** Because a DTO and a Domain Model look different! The Mapper bridges the gap safely. All mappers inherit from `BaseMapper` to keep our code consistent.

---

## 🚀 How a Request Flows

Here is exactly what happens when a user calls `POST /api/v1/order`:

1. **User sends JSON payload:** The user sends a complex JSON object containing product details and credit card info.
2. **FastAPI Route receives it & DTO validates it:** The router (`app/api/v1/routes/orders.py`) catches it. FastAPI automatically uses `app/dto/order_request.py` to validate that the JSON is perfectly matched to our API rules.
3. **The Mapper translates it:** The route handler gives the DTO to `OrderMapper.to_domain(req)`. The mapper transforms the messy, API-specific properties into a pristine `Order` Domain object.
4. **Business Logic runs:** We now pass the clean `Order` Domain object into our Services or Repositories to process the payment, save to the database, etc.

---

## 🛠 How to Create a New Feature (Cheat Sheet)

Let's say you're asked to build a new `Invoice` feature. Follow these steps:

### Step 1: Create the DTO
Create a file at `app/dto/invoice_request.py`. Define exactly what JSON the user should POST to the API.
```python
from pydantic import BaseModel

class InvoiceRequest(BaseModel):
    user_id: str
    total_amount: float
```

### Step 2: Create the Domain Entity
Create a file at `app/domain/invoice.py`. Define the pure business entity.
```python
from pydantic import BaseModel

class Invoice(BaseModel):
    id: str # We might generate this internally!
    user_id: str
    total_amount: float
    status: str = "PENDING"
```

### Step 3: Create the Mapper
Create a file at `app/mappers/invoice_mapper.py`. It MUST inherit from `BaseMapper`!
```python
from app.core.base_mapper import BaseMapper
from app.dto.invoice_request import InvoiceRequest
from app.domain.invoice import Invoice
import uuid

class InvoiceMapper(BaseMapper[InvoiceRequest, Invoice]):
    
    @staticmethod
    def to_domain(dto: InvoiceRequest) -> Invoice:
        # We manually bridge the two here!
        return Invoice(
            id=str(uuid.uuid4()),  # Internal business logic
            user_id=dto.user_id,
            total_amount=dto.total_amount
        )
```

### Step 4: Add the Route
Create `app/api/v1/routes/invoices.py` and bring it all together.
```python
from fastapi import APIRouter
from app.dto.invoice_request import InvoiceRequest
from app.mappers.invoice_mapper import InvoiceMapper

router = APIRouter()

@router.post("/invoices")
def create_invoice(req: InvoiceRequest):
    # 1. DTO automatically validates `req` here.
    
    # 2. Map the DTO to the pure Domain entity
    invoice_domain_model = InvoiceMapper.to_domain(req)
    
    # 3. Save to DB or run business logic using `invoice_domain_model`
    
    return {"status": "success", "data": invoice_domain_model.model_dump()}
```

---

## 🎯 Summary
By adding slightly more code upfront (Mappers and DTOs), we guarantee that if the mobile or web app frontend suddenly wants a differently formatted JSON payload next month, we only change the **DTO** and **Mapper**. Our core business **Domain Entities** and Database stay perfectly safe and completely untouched!
