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
from invenio_i18n import lazy_gettext as _

import invenio_pidstore_extra.providers as providers
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
        PIDSTORE_EXTRA_DNB_SANDBOX_URI="http://localhost:8000/",
        PIDSTORE_EXTRA_DNB_USERNAME=username,
        PIDSTORE_EXTRA_DNB_PASSWORD=password,
        PIDSTORE_EXTRA_DNB_ID_PREFIX=prefix,
        PIDSTORE_EXTRA_FORMAT="{prefix}-{id}",
        PIDSTORE_EXTRA_TEST_MODE=True,
        PIDSTORE_EXTRA_DNB_ENABLED=True,
        RDM_PERSISTENT_IDENTIFIER_PROVIDERS=[
            providers.DnbUrnProvider(
                "urn",
                client=providers.DNBUrnClient(
                    "dnb", prefix, username, password, "{prefix}-{id}"
                ),
                label=_("URN"),
            ),
        ],
        RDM_PERSISTENT_IDENTIFIERS={
            "urn": {
                "providers": ["urn"],
                "required": True,
                "label": _("URN"),
                "is_enabled": providers.DnbUrnProvider.is_enabled,
            },
        },
    )

    return app_


@pytest.fixture()
def app(base_app, request):
    """Flask application fixture."""
    return base_app


@pytest.fixture()
def client(app):
    """Create an API client."""
    client = DNBUrnServiceRESTClient(
        username=app.config["PIDSTORE_EXTRA_DNB_USERNAME"],
        password=app.config["PIDSTORE_EXTRA_DNB_PASSWORD"],
        prefix=app.config["PIDSTORE_EXTRA_DNB_ID_PREFIX"],
        test_mode=True,
    )
    return client
