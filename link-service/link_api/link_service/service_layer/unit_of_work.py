import abc

from link_service.repository import AbstractLinkRepository


class AbstractUnitOfWork(abc.ABC):
    links: AbstractLinkRepository

    def __init__(
            self,
            links: AbstractLinkRepository = None
    ):
        self.links = links

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
