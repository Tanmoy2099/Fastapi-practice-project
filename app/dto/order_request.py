from typing import List, Literal, Union

from pydantic import BaseModel, Field


# ---------- PRODUCT ----------
class IncomingProduct(BaseModel):
    id: str
    price: float
    quantity: int


# ---------- PRICING ----------
class IncomingPricing(BaseModel):
    tax: float
    discount: float | None = None


# ---------- META ----------
class IncomingMetaPrice(BaseModel):
    history: List[float]
    current: float


class IncomingMetaExternal(BaseModel):
    id: str


class IncomingMeta(BaseModel):
    external: IncomingMetaExternal
    price: IncomingMetaPrice


# ---------- MAIN DATA ----------
class IncomingData(BaseModel):
    product: IncomingProduct
    pricing: IncomingPricing
    meta: IncomingMeta

    instanceId: str
    totalPrice: float
    actualPrice: float


# ---------- PAYMENT (DISCRIMINATED UNION) ----------
class CardPayment(BaseModel):
    payment_type: Literal["card"]
    card_number: str
    cvv: str
    save_card: bool | None = None


class PaypalPayment(BaseModel):
    payment_type: Literal["paypal"]
    paypal_token: str


class GPayPayment(BaseModel):
    payment_type: Literal["gpay"]
    gpay_token: str


PaymentMethod = Union[CardPayment, PaypalPayment, GPayPayment]


# ---------- ROOT REQUEST ----------
class OrderRequest(BaseModel):
    data: IncomingData
    payment: PaymentMethod = Field(..., discriminator="payment_type")
