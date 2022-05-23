import dataclasses

from app.order_line import OrderLine


@dataclasses.dataclass(eq=False)
class Batch:
    def __init__(self, reference, sku, quantity, eta) -> None:
        self.reference = reference
        self.sku = sku
        self.quantity = quantity
        self.eta = eta
        self._order_lines = set()

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def allocate(self, order_line: OrderLine):
        self.quantity -= order_line.quantity
        self._order_lines.add(order_line)

    @property
    def available_quantity(self):

        return self.quantity - sum([ol.quantity for ol in self._order_lines])

    def can_allocate(self, order_line):
        if self.sku == order_line.sku:
            return self.quantity >= order_line.quantity
        return False

    def deallocate(self, order_line: OrderLine):
        if order_line in self._order_lines:
            self._order_lines.remove(order_line)


class AllocateException(Exception):
    pass
