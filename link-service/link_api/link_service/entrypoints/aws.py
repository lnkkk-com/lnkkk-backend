import json
import os
import sys

from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide

from link_service.data import LINK_DATA
from link_service.repository import AbstractLinkRepository, DynamoDBLinkRepository


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    link_repository = providers.Factory(
        DynamoDBLinkRepository,
        table_name=config.table_name,
        is_local=config.is_local,
    )


@inject
def link_list(
    event,
    context,
    link_repository: AbstractLinkRepository = Provide[Container.link_repository],
):
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "data": link_repository.get_list(),
            }
        ),
    }


@inject
def link_create(
    event,
    context,
    link_repository: AbstractLinkRepository = Provide[Container.link_repository],
):
    payload = json.loads(event["body"])
    link = link_repository.create(title=payload.get("title"), url=payload.get("url"))
    if not link:
        return {"statusCode": 400, "body": json.dumps({"message": "failed"})}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "data": link,
            }
        ),
    }


@inject
def link_delete(
    event,
    context,
    link_repository: AbstractLinkRepository = Provide[Container.link_repository],
):
    link_id = event["pathParameters"]["id"]
    link_repository.delete(link_id)

    return {
        "statusCode": 200,
        "body": json.dumps({}),
    }


@inject
def link_detail(
    event,
    context,
    link_repository: AbstractLinkRepository = Provide[Container.link_repository],
):
    link_id = event["pathParameters"]["id"]
    link = link_repository.get(link_id)
    if not link:
        return {"statusCode": 404, "body": json.dumps({"message": "not found"})}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "data": link,
            }
        ),
    }


@inject
def link_update(
    event,
    context,
    link_repository: AbstractLinkRepository = Provide[Container.link_repository],
):
    link_id = event["pathParameters"]["id"]
    payload = json.loads(event["body"])
    link = link_repository.update(
        link_id, title=payload.get("title"), url=payload.get("url")
    )
    if not link:
        return {"statusCode": 404, "body": json.dumps({"message": "not found"})}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "data": link,
            }
        ),
    }


def lambda_handler(event, context):
    request_context = event["requestContext"]
    path = request_context["resourcePath"]
    http_method = request_context["httpMethod"]

    container = Container()
    is_local = os.environ.get("AWS_SAM_LOCAL") == "true"
    container.config.from_dict(
        {
            "is_local": is_local,
            "table_name": os.environ.get("TABLE_NAME") if not is_local else "TodoTable",
        }
    )
    container.wire(modules=[sys.modules[__name__]])

    routes = {
        ("GET", "/links"): link_list,
        ("GET", "/links/{id}"): link_detail,
        ("POST", "/links"): link_create,
        ("PUT", "/links/{id}"): link_update,
        ("DELETE", "/links/{id}"): link_delete,
    }

    try:
        return routes[(http_method, path)](
            event,
            context,
        )
    except Exception as e:
        print(type(e), str(e))
        return {
            "statusCode": 404,
            "body": json.dumps(
                {
                    "message": "not found",
                    "path": path,
                    "httpMethod": http_method,
                    "requestContext": request_context,
                }
            ),
        }
