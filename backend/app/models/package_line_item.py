from enum import StrEnum

from sqlmodel import Field, SQLModel


class ProductType(StrEnum):
    PAPER_PRODUCT = "paper_product"
    OFFICE_SUPPLY = "office_supply"


class PackageLineItem(SQLModel, table=True):
    __tablename__ = "package_line_item"

    id: int | None = Field(default=None, primary_key=True)
    package_id: str = Field(foreign_key="package.package_id", index=True, max_length=100)
    product_name: str = Field(max_length=300)
    product_category: str = Field(max_length=200)
    quantity: int = Field(ge=1)
    unit_description: str = Field(max_length=200)
    product_type: str = Field(max_length=50)
    fragile: bool = Field(default=False)
