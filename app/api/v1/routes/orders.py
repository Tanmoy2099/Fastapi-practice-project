from fastapi import APIRouter
from app.dto.order_request import OrderRequest
from app.mappers.order_mapper import OrderMapper

router = APIRouter()

@router.post("/order", summary="Create order using clean architecture mapping")
def create_order(req: OrderRequest):
    # Map the validated DTO request to the pristine Domain model
    order = OrderMapper.to_domain(req)

    # Note: Pure business logic execution goes here...
    
    return {
        "status": "success",
        "message": "Order mapped successfully into domain model",
        "data": order.model_dump()
    }
