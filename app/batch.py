import dataclasses
import datetime

from app.order_line import OrderLine


@dataclasses.dataclass(eq=False)
class Batch:
    id: str
    product_name: str
    qty: int
    eta: datetime.date

    def allocate(self, order_line: OrderLine):
        if self.qty < order_line.quantity:
            raise AllocateException()
        self.qty -= order_line.quantity

    @property
    def available_quantity(self):
        return self.qty


class AllocateException(Exception):
    pass
