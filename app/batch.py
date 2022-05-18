import dataclasses
import datetime

from app.order_line import OrderLine


@dataclasses.dataclass(eq=False)
class Batch:
    reference: str
    sku: str
    quantity: int
    eta: datetime.date

    def allocate(self, order_line: OrderLine):
        if self.quantity < order_line.quantity:
            raise AllocateException()
        self.quantity -= order_line.quantity

    @property
    def available_quantity(self):
        return self.quantity

    def can_allocate(self, order_line):
        if self.sku == order_line.sku:
            return self.quantity >= order_line.quantity
        return False


class AllocateException(Exception):
    pass
