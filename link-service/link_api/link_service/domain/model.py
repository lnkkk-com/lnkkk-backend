from dataclasses import dataclass


@dataclass
class Link:
    id: str
    title: str
    href: str

    @classmethod
    def from_dict(cls, a_dict=None, **kwargs):
        if not a_dict:
            a_dict = kwargs

        return cls(
            id=a_dict.get("id"),
            title=a_dict.get("title"),
            href=a_dict.get("href"),
        )
