from pydantic import BaseModel
from typing import List

class Product(BaseModel):
    id: str
    price: float
    quantity: int

class MetaPrice(BaseModel):
    old_prices: List[float]
    new_price: float

class Meta(BaseModel):
    external_id: str
    price: MetaPrice

class Payment(BaseModel):
    method: str
    details: dict

class Order(BaseModel):
    product: Product
    tax: float
    discount: float | None
    instance_id: str
    total_price: float
    actual_price: float
    meta: Meta
    payment: Payment
