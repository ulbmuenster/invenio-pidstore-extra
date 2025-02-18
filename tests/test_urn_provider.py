# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Tests for DNB api wrapper."""

import random
import sys

import pytest

from invenio_pidstore_extra.providers.urn.errors import (
    DNBURNServiceConflictError,
    DNBURNServiceUrnNotRegisteredError,
    DNBURNServiceUserNotAuthorizedError,
)


def test_urn_post(app, client):
    """Test."""
    i = None
    result = 200
    while result == 200:
        i = random.randint(1, sys.maxsize)
        try:
            result = client.check_if_registered("urn:nbn:de:hbz:6-" + str(i))
        except DNBURNServiceUrnNotRegisteredError:
            result = 404
    result = client.create_urn(
        "https://test.org/" + str(i) + ".pdf", "urn:nbn:de:hbz:6-" + str(i)
    )
    assert result == "urn:nbn:de:hbz:6-" + str(i)


def test_urn_get_403(app, client):
    """Test."""
    with pytest.raises(DNBURNServiceUserNotAuthorizedError):
        client.get_urn("urn:nbn:de:hbz:6-1")


def test_urn_get_404(app, client):
    """Test."""
    with pytest.raises(DNBURNServiceUrnNotRegisteredError):
        client.get_urn("urn:nbn:de:hbz:6-123")


def test_urn_post_409(app, client):
    """Test."""
    with pytest.raises(DNBURNServiceConflictError):
        _ = client.create_urn("https://test.org/abc.pdf", "urn:nbn:de:hbz:6-1")


def test_urn_delete(app, client):
    """Test."""
    with pytest.raises(DNBURNServiceUserNotAuthorizedError):
        client.delete_urn("urn:nbn:de:hbz:6-1")
