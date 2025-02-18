# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import os
import tempfile

import pytest
from flask import Flask

from invenio_pidstore_extra.providers.urn import DNBUrnServiceRESTClient


@pytest.fixture()
def base_app():
    """Flask base application fixture."""
    instance_path = tempfile.mkdtemp()
    username = os.environ["PIDSTORE_EXTRA_DNB_USERNAME"]
    password = os.environ["PIDSTORE_EXTRA_DNB_PASSWORD"]
    prefix = os.environ["PIDSTORE_EXTRA_DNB_ID_PREFIX"]
    app_ = Flask("testapp", instance_path=instance_path)
    app_.config.update(
        PIDSTORE_EXTRA_DNB_USERNAME=username,
        PIDSTORE_EXTRA_DNB_PASSWORD=password,
        PIDSTORE_EXTRA_DNB_ID_PREFIX=prefix,
        PIDSTORE_EXTRA_FORMAT="{prefix}-{id}",
        PIDSTORE_EXTRA_TEST_MODE=True,
        PIDSTORE_EXTRA_DNB_ENABLED=True,
    )

    return app_


@pytest.fixture()
def app(base_app, request):
    """Flask application fixture."""
    return base_app


@pytest.fixture(scope="module")
def client(app):
    """Create an API client."""
    client = DNBUrnServiceRESTClient(
        username=app.config["PIDSTORE_EXTRA_DNB_USERNAME"],
        password=app.config["PIDSTORE_EXTRA_DNB_PASSWORD"],
        prefix=app.config["PIDSTORE_EXTRA_DNB_ID_PREFIX"],
        test_mode=True,
    )
    return client
