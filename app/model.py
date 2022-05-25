import datetime
from app.batch import Batch
from app.order_line import OrderLine
from typing import List


def allocate(line: OrderLine, batches: List[Batch]):
    earlier_batch = __get_earlier_batch(batches)
    earlier_batch.allocate(line)
    return earlier_batch.reference


def __get_earlier_batch(batches):
    return sorted(batches, key=__get_eta_from_batch)[0]


def __get_eta_from_batch(batch):
    if batch.eta is None:
        return datetime.date.fromtimestamp(0)
    return batch.eta
