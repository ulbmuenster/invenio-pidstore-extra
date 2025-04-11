# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Simple implementation of DNB URN API."""

import base64
import random

import arrow
from flask import Flask, jsonify, request

app = Flask(__name__)
namespace = "urn:nbn:de:hbz:6-"


@app.route("/namespaces/name/<name>", methods=["GET"])
def namespace_info(name: str):
    """Implementation of namespaces API."""
    now = arrow.utcnow().isoformat()
    return jsonify(
        {
            "name": name,
            "created": now,
            "lastModified": now,
            "allowsRegistration": True,
            "owner": "http://localhost:8000/organisations/id/1",
            "urnNamingPolicy": "http://localhost:8000/policies/urn-naming/id/no-check",
            "urlPolicy": "http://localhost:8000/policies/url/id/no-check",
            "resolverUrl": "",
            "urns": request.url + "/urns",
            "urnSuggestion": request.url + "/urn-suggestion",
            "self": request.url,
        }
    )


@app.route("/namespaces/name/<name>/urn-suggestion", methods=["GET"])
def suggest(name: str):
    """Implementation of suggest API."""
    return jsonify(
        {
            "suggestedUrn": name + str(random.randrange(1000000000, 9999999999, 1)),
            "namespace": request.url[: request.url.find("/urn-suggestion")],
            "self": request.url,
        }
    )


@app.route("/urns", methods=["POST"])
def register():
    """Implementation of URN registration API."""
    now = arrow.utcnow().isoformat()
    content = request.json
    return (
        jsonify(
            {
                "urn": content["urn"],
                "created": now,
                "lastModified": now,
                "namespace": "http://localhost:8000/namespaces/name/" + namespace,
                "successor": None,
                "urls": request.url + "/urn/" + content["urn"] + "/urls",
                "myUrls": request.url + "/urn/" + content["urn"] + "/my-urls",
                "self": request.url + "/urn/" + content["urn"],
            }
        ),
        201,
    )


@app.route("/urns/urn/<urn>", methods=["HEAD"])
def check_existence(urn: str):
    """Implementation of check for existence API."""
    if urn.startswith(namespace):
        suffix = urn[len(namespace) :]
        if int(suffix) < 5000000000:
            return "", 200
    return "", 404


@app.route("/urns/urn/<urn>", methods=["GET"])
def get_urn(urn: str):
    """Implementation of get URN API."""
    if urn.startswith(namespace):
        suffix = urn[len(namespace) :]
        if int(suffix) < 5000000000:
            now = arrow.utcnow().isoformat()
            return jsonify(
                {
                    "urn": urn,
                    "created": now,
                    "lastModified": now,
                    "namespace": "http://localhost:8000/namespaces/name/" + namespace,
                    "successor": None,
                    "urls": request.url + "/urls",
                    "myUrls": request.url + "/my-urls",
                    "self": request.url,
                }
            )
    return "", 404


@app.route("/urns/urn/<urn>/urls", methods=["GET"])
def get_url(urn: str):
    """Implementation of get URL API."""
    return get_urls(urn, "/urls")


@app.route("/urns/urn/<urn>/my-urls", methods=["GET"])
def get_my_url(urn: str):
    """Implementation of get my URL API."""
    return get_urls(urn, "/my-urls")


@app.route("/urns/urn/<urn>/urls/base64/<encoded>", methods=["GET"])
def get_single_url(urn: str, encoded: str):
    """Implementation of get single URL API."""
    now = arrow.utcnow().isoformat()
    return jsonify(
        {
            "url": base64.b64decode(bytes(encoded, "utf-8")).decode("utf-8"),
            "created": now,
            "lastModified": now,
            "urn": request.url[: request.url.find("/urls")],
            "owner": "http://localhost:8000/organisations/id/1",
            "priority": 10,
            "self": request.url,
        }
    )


@app.route("/urns/urn/<urn>/urls", methods=["POST"])
def add_url(urn: str):
    """Implementation of add URL API."""
    now = arrow.utcnow().isoformat()
    content = request.json
    return jsonify(
        {
            "url": content["url"],
            "created": now,
            "lastModified": now,
            "urn": request.url[: request.url.find("/urls")],
            "owner": "http://localhost:8000/organisations/id/1",
            "priority": 10,
            "self": request.url
            + "/urls/base64/"
            + base64.b64encode(bytes(content["url"], "utf-8")).decode("utf-8"),
        }
    )


@app.route("/urns/urn/<urn>/urls/base64/<encoded>", methods=["DELETE"])
def remove_url(urn: str, encoded: str):
    """Implementation of remove URL API."""
    return "", 204


@app.route("/urns/urn/<urn>/my-urls", methods=["PATCH"])
def add_my_url(urn: str):
    """Implementation of add my URL API."""
    return "", 204


@app.route("/urns/urn/<urn>", methods=["PATCH"])
def set_successor(urn: str):
    """Implementation of set successor  API."""
    return "", 204


def get_urls(urn: str, query: str):
    """Helper method."""
    if urn.startswith(namespace):
        suffix = urn[len(namespace) :]
        if int(suffix) < 5000000000:
            now = arrow.utcnow().isoformat()
            find_urls = request.url.rfind(query)
            return jsonify(
                {
                    "totalItems": 1,
                    "items": [
                        {
                            "url": "http://example.org/document-url",
                            "created": now,
                            "lastModified": now,
                            "urn": request.url[:find_urls],
                            "owner": "http://localhost:8000/organisations/id/1",
                            "priority": 10,
                            "self": request.url[:find_urls]
                            + "/urls/base64/aHR0cDovL2V4YW1wbGUub3JnL2RvY3VtZW50LXVybA==",
                        }
                    ],
                    "self": request.url,
                }
            )
    return "", 404


if __name__ == "__main__":
    app.run()
