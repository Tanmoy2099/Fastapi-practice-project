from app.core.base_mapper import BaseMapper
from app.dto.order_request import (
    OrderRequest,
    CardPayment,
    PaypalPayment,
    GPayPayment
)
from app.domain.order import (
    Order,
    Product,
    Meta,
    MetaPrice,
    Payment
)

class OrderMapper(BaseMapper[OrderRequest, Order]):
    
    @staticmethod
    def to_domain(req: OrderRequest) -> Order:
        d = req.data

        # 🔥 Payment mapping (polymorphic handling)
        if isinstance(req.payment, CardPayment):
            payment = Payment(
                method="card",
                details={
                    "card_number": req.payment.card_number,
                    "cvv": req.payment.cvv,
                    "save_card": req.payment.save_card,
                }
            )

        elif isinstance(req.payment, PaypalPayment):
            payment = Payment(
                method="paypal",
                details={
                    "token": req.payment.paypal_token
                }
            )

        elif isinstance(req.payment, GPayPayment):
            payment = Payment(
                method="gpay",
                details={
                    "token": req.payment.gpay_token
                }
            )

        else:
            raise ValueError("Unsupported payment type")

        return Order(
            product=Product(**d.product.model_dump()),
            tax=d.pricing.tax,
            discount=d.pricing.discount,
            instance_id=d.instanceId,
            total_price=d.totalPrice,
            actual_price=d.actualPrice,
            meta=Meta(
                external_id=d.meta.external.id,
                price=MetaPrice(
                    old_prices=d.meta.price.history,
                    new_price=d.meta.price.current,
                ),
            ),
            payment=payment
        )

    @staticmethod
    def to_dto(domain: Order) -> OrderRequest:
        raise NotImplementedError("Mapping Domain to DTO is not needed in this flow.")
