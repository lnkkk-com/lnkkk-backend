import abc
import uuid


class AbstractLinkRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, link_id: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get_list(
        self,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, title=None, url=None):
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, link_id, title=None, url=None):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, link_id):
        raise NotImplementedError


class MemLinkRepository(AbstractLinkRepository):
    def __init__(self, links):
        self.links = links

    def create(self, title=None, url=None):
        if title is None:
            raise ValueError

        link = {
            "id": str(uuid.uuid4()),
            "title": title,
            "url": url,
        }
        self.links.append(link)
        return link

    def update(self, link_id, title, url):
        link = self.get(link_id)
        if link is None:
            return None

        link["title"] = title
        link["url"] = url
        self.links = [
            link if str(item["id"]) == str(link_id) else item for item in self.links
        ]

        return link

    def delete(self, link_id):
        self.links = list(
            filter(lambda obj: str(obj["id"]) != str(link_id), self.links)
        )

    def get(self, link_id):
        try:
            return next(link for link in self.links if str(link["id"]) == str(link_id))
        except StopIteration:
            return None

    def get_list(
        self,
    ):
        return self.links
