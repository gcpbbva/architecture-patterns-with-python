import dataclasses


@dataclasses.dataclass(eq=False)
class OrderLine:
    order_ref: str
    product_name: str
    quantity: int
