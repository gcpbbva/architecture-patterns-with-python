import datetime
from typing import List

from app.batch import Batch
from app.order_line import OrderLine


def allocate(line: OrderLine, batches: List[Batch]):
    earlier_batch = __get_earlier_batch(line, batches)
    earlier_batch.allocate(line)
    return earlier_batch.reference


def __get_earlier_batch(line: OrderLine, batches: List[Batch]):
    valid_batches_to_allocate_line = [batch for batch in batches if batch.can_allocate(order_line=line)]
    if not valid_batches_to_allocate_line:
        raise OutOfStock(line.sku)
    return sorted(valid_batches_to_allocate_line, key=__get_eta_from_batch)[0]


def __get_eta_from_batch(batch: Batch):
    if batch.eta is None:
        return datetime.date.fromtimestamp(0)
    return batch.eta


class OutOfStock(Exception):
    pass
