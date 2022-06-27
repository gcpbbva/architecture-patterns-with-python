import pytest

from app import services, model
from tests import FakeRepository, FakeSession


def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True


def test_allocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo)
    line = model.OrderLine("o1", "BLUE-PLINTH", 10)

    services.allocate(line, repo, session)

    batch = repo.get(reference="b1")
    assert batch.available_quantity == 90


def test_deallocate_increments_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo)
    line = model.OrderLine("o1", "BLUE-PLINTH", 10)
    services.allocate(line, repo, session)

    services.deallocate("b1", line, repo)

    batch = repo.get(reference="b1")
    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo)
    line = model.OrderLine("o1", "BLUE-PLINTH", 10)
    line_2 = model.OrderLine("o2", "WHITE-PLINTH", 10)
    services.allocate(line, repo, session)

    services.deallocate("b1", line_2, repo)

    batch = repo.get(reference="b1")
    assert batch.available_quantity == 90


def test_trying_to_deallocate_unallocated_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo)
    line = model.OrderLine("o1", "BLUE-PLINTH", 10)

    services.deallocate("b1", line, repo)

    batch = repo.get(reference="b1")
    assert batch.available_quantity == 100
