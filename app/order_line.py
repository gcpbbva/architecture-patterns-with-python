import dataclasses


@dataclasses.dataclass(eq=False)
class OrderLine:
    order_reference: str
    sku: str
    quantity: int
