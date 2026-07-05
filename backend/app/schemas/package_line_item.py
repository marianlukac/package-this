from pydantic import BaseModel


class LineItemCreate(BaseModel):
    product_name: str
    product_category: str
    quantity: int
    unit_description: str
    product_type: str
    fragile: bool = False


class LineItemUpdate(BaseModel):
    product_name: str | None = None
    product_category: str | None = None
    quantity: int | None = None
    unit_description: str | None = None
    product_type: str | None = None
    fragile: bool | None = None


class LineItemResponse(BaseModel):
    id: int
    package_id: str
    product_name: str
    product_category: str
    quantity: int
    unit_description: str
    product_type: str
    fragile: bool
