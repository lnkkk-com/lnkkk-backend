import abc
import uuid

import boto3
from botocore.exceptions import ClientError


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
    def create(self, title=None, href=None):
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, link_id, title=None, href=None):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, link_id):
        raise NotImplementedError


class MemLinkRepository(AbstractLinkRepository):
    def __init__(self, links):
        self.links = links

    def create(self, title=None, href=None):
        if title is None:
            raise ValueError

        link = {
            "id": str(uuid.uuid4()),
            "title": title,
            "href": href,
        }
        self.links.append(link)
        return link

    def update(self, link_id, title=None, href=None):
        link = self.get(link_id)
        if link is None:
            return None

        link["title"] = title
        link["href"] = href
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


class DynamoDBLinkRepository(AbstractLinkRepository):
    def __init__(self, table_name, is_local=False):
        if is_local:
            dynamodb = boto3.resource("dynamodb", endpoint_url="http://dynamodb:8000")
        else:
            dynamodb = boto3.resource("dynamodb")

        self.table = dynamodb.Table(
            table_name,
        )

    def get(self, link_id: str):
        try:
            resp = self.table.get_item(
                Key={
                    "id": link_id,
                }
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            return resp.get("Item")

    def get_list(self):
        resp = self.table.scan()
        return resp.get("Items", [])

    def create(self, title=None, href=None):
        try:
            link_id = str(uuid.uuid4())
            self.table.put_item(
                Item={
                    "id": link_id,
                    "title": title,
                    "href": href,
                }
            )
        except Exception as e:
            print(type(e), str(e))
            return False

        return self.get(link_id)

    def update(self, link_id, title=None, href=None):
        try:
            self.table.update_item(
                Key={
                    "id": link_id,
                },
                UpdateExpression="set title=:t, href=:h",
                ExpressionAttributeValues={
                    ":t": title,
                    ":h": href,
                },
                ReturnValues="UPDATED_NEW",
            )
        except Exception as e:
            print(type(e), str(e))
            return False

        return self.get(link_id)

    def delete(self, link_id):
        try:
            resp = self.table.delete_item(
                Key={
                    "id": link_id,
                },
            )
        except ClientError as e:
            print(type(e), str(e))
            return False
        else:
            return resp
