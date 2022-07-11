# pylint: disable=attribute-defined-outside-init
from __future__ import annotations

import abc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config
from allocation.adapters import repository


class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, exn_type, *args):
        if exn_type is None:
            self.commit()
        else:
            self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)


def start(session_factory):
    return SqlAlchemyUnitOfWork(session_factory)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.batches = repository.SqlAlchemyRepository(session=self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

# One alternative would be to define a `start_uow` function,
# or a UnitOfWorkStarter or UnitOfWorkManager that does the
# job of context manager, leaving the UoW as a separate class
# that's returned by the context manager's __enter__.
#
# A type like this could work?
# AbstractUnitOfWorkStarter = ContextManager[AbstractUnitOfWork]
