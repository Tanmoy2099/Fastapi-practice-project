# FastAPI Code Patterns & Cheatsheet

This file contains practical **Code** examples for how to execute common tasks in an enterprise FastAPI project.

## 1. Writing a Route using Dependency Injection
Dependency Injection (`Depends()`) lets you pull in database sessions, current users, or configuration instantly without writing boilerplate.

```python
from fastapi import APIRouter, Depends
from typing import Annotated

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify token...
    return user

@router.get("/users/me")
def read_current_user(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user
```

## 2. Returning Standardized Success/Error Responses
Enterprise APIs often wrap their data in a standardized envelope:
```python
from pydantic import BaseModel
from typing import Generic, TypeVar

DataT = TypeVar('DataT')

class ApiResponse(BaseModel, Generic[DataT]):
    status: str = "success"
    data: DataT
```

## 3. Global Exception Handling
Catch exceptions globally so users never see a nasty 500 internal stack trace.
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An unexpected error occurred."}
    )
```
