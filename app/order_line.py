import dataclasses


@dataclasses.dataclass(frozen=True)
class OrderLine:
    order_reference: str
    sku: str
    quantity: int
