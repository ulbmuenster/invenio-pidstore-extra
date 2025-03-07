# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Tests for DNB wrapper."""
import json
from unittest.mock import patch

import pytest

from invenio_pidstore_extra.providers.urn.errors import (
    DNBURNServiceConflictError,
    DNBURNServiceUrnNotRegisteredError,
    DNBURNServiceUserNotAuthorizedError,
)
from invenio_pidstore_extra.providers.urn.rest import DNBUrnServiceRESTClient


@pytest.fixture()
def dnb_rest_client():
    """DNBUrnServiceRESTClient fixture."""
    return DNBUrnServiceRESTClient("username", "password", "urn:nbn:de:hbz:6", True)


@patch("invenio_pidstore_extra.providers.urn.request.requests.get")
def test_provider_rest_get_urn(mock_get, dnb_rest_client):
    """Test REST get."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "totalItems": 1,
        "items": [
            {
                "url": "https://www.test-succeeded.com/",
                "created": "2019-02-13T15:32:48.123Z",
                "lastModified": "2019-02-13T15:32:48.123Z",
                "urn": "https://api.nbn-resolving.org/sandbox/v2/urns/urn/urn:nbn:de:example-2019021315155244513532",
                "owner": "https://api.nbn-resolving.org/sandbox/v2/organisations/id/1",
                "priority": 10,
                "self": "https://api.nbn-resolving.org/sandbox/v2/urns/urn/urn:nbn:de:example-2019021315155244513532/urls/base64/aHR0cDovL2V4YW1wbGUub3JnL2RvY3VtZW50LXVybA==",
            },
            {
                "url": "https://www.test-failed.com/",
                "created": "2019-02-13T15:32:48.123Z",
                "lastModified": "2019-02-13T15:32:48.123Z",
                "urn": "https://api.nbn-resolving.org/sandbox/v2/urns/urn/urn:nbn:de:example-2019021315155244513532",
                "owner": "https://api.nbn-resolving.org/sandbox/v2/organisations/id/1",
                "priority": 10,
                "self": "https://api.nbn-resolving.org/sandbox/v2/urns/urn/urn:nbn:de:example-2019021315155244513532/urls/base64/aHR0cDovL2V4YW1wbGUub3JnL2RvY3VtZW50LXVybA==",
            },
        ],
        "self": "https://api.nbn-resolving.org/sandbox/v2/urns/urn/urn:nbn:de:example-2019021315155244513532/my-urls",
    }
    response = dnb_rest_client.get_urn("urn:nbn:xyz")
    assert response == "https://www.test-succeeded.com/"


@patch("invenio_pidstore_extra.providers.urn.request.requests.get")
def test_provider_rest_get_urn_403(mock_get, dnb_rest_client):
    """Test REST get."""
    mock_get.return_value.status_code = 403
    with pytest.raises(DNBURNServiceUserNotAuthorizedError):
        _ = dnb_rest_client.get_urn("urn:nbn:xyz")


@patch("invenio_pidstore_extra.providers.urn.request.requests.get")
def test_provider_rest_get_urn_404(mock_get, dnb_rest_client):
    """Test REST get."""
    mock_get.return_value.status_code = 404
    with pytest.raises(DNBURNServiceUrnNotRegisteredError):
        _ = dnb_rest_client.get_urn("urn:nbn:xyz")


@patch("invenio_pidstore_extra.providers.urn.request.requests.post")
def test_provider_rest_create_urn(mock_post, dnb_rest_client):
    """Test REST create_urn."""
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {
        "urn": "urn:nbn:de:hbz:6-xyz",
        "created": "2019-02-13T15:32:48.123Z",
        "lastModified": "2019-02-13T15:32:48.123Z",
        "namespace": "https://api.nbn-resolving.org/sandbox/v2/namespaces/name/urn:nbn:de",
        "successor": None,
        "urls": "https://api.nbn-resolving.org/sandbox/v2/urns/urn/urn:nbn:de:hbz:6-xyz/urls",
        "myUrls": "https://api.nbn-resolving.org/sandbox/v2/urns/urn/urn:nbn:de:hbz:6-xyz/my-urls",
        "self": "https://api.nbn-resolving.org/sandbox/v2/urns/urn/urn:nbn:de:hbz:6-xyz",
    }
    result = dnb_rest_client.create_urn(
        "https://test.org/test.pdf", "urn:nbn:de:hbz:6-xyz"
    )
    assert result == "urn:nbn:de:hbz:6-xyz"


@patch("invenio_pidstore_extra.providers.urn.request.requests.post")
def test_provider_rest_create_urn_409(mock_post, dnb_rest_client):
    """Test REST create_urn."""
    mock_post.return_value.status_code = 409
    with pytest.raises(DNBURNServiceConflictError):
        _ = dnb_rest_client.create_urn("https://test.org/abc.pdf", "urn:nbn:de:hbz:6-1")


@patch("invenio_pidstore_extra.providers.urn.request.requests.head")
def test_provider_rest_check_urn_is_registered(mock_head, dnb_rest_client):
    """Test REST check_is_registered."""
    mock_head.return_value.status_code = 200
    urn = dnb_rest_client.check_if_registered("urn:nbn:de:hbz:6-xyz")

    assert urn == "urn:nbn:de:hbz:6-xyz"


@patch("invenio_pidstore_extra.providers.urn.request.requests.head")
def test_provider_rest_check_urn_not_registered(mock_head, dnb_rest_client):
    """Test REST check_is_registered."""
    mock_head.return_value.status_code = 404
    with pytest.raises(DNBURNServiceUrnNotRegisteredError):
        dnb_rest_client.check_if_registered("urn:nbn:xyz")


@patch("invenio_pidstore_extra.providers.urn.request.requests.patch")
def test_provider_rest_create_successor(mock_patch, dnb_rest_client):
    """Test REST check_is_registered."""
    mock_patch.return_value.status_code = 204
    mock_patch.return_value.json.return_value = {
        "successor": "https://api.nbn-resolving.org/sandbox/v2/urns/urn/urn:nbn:de:hbz:6-abc",
    }
    response = dnb_rest_client.create_successor(
        "urn:nbn:de:hbz:6-xyz", "urn:nbn:de:hbz:6-abc"
    )
    assert response == ""


@patch("invenio_pidstore_extra.providers.urn.request.requests.patch")
def test_provider_rest_remove_successor(mock_patch, dnb_rest_client):
    """Test REST check_is_registered."""
    mock_patch.return_value.status_code = 204
    response = dnb_rest_client.remove_successor("urn:nbn:de:hbz:6-xyz")
    mock_patch.return_value.json.return_value = {
        "successor": None,
    }
    assert response == ""
