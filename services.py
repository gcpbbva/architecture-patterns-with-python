from __future__ import annotations

import model
from model import OrderLine
from repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref

def add_batch(batch_reference, sku, qty, eta, repo, session):
    new_batch = model.Batch(batch_reference, sku, qty, eta)
    repo.add(new_batch)

def deallocate(batch_reference, line, repo):
    batch = repo.get(reference=batch_reference)
    batch.deallocate(line=line)
