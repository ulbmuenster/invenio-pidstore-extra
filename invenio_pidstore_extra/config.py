# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module that adds URN minting by DNB epicur service."""

PIDSTORE_EXTRA_DNB_ENABLED = True
"""The URN provider is by default enabled (or why would you have installed the module?)."""

PIDSTORE_EXTRA_TEST_MODE = True
"""Set to 'False' if you want to mint real URN's."""

PIDSTORE_EXTRA_DNB_USERNAME = "username"
"""A username provided for you by DNB if you have a legal contract."""

PIDSTORE_EXTRA_DNB_PASSWORD = "password"
"""The corresponding password."""

PIDSTORE_EXTRA_DNB_ID_PREFIX = "urn:nbn:dnb:provider:"
"""Just an example! Please replace by prefix provided by DNB."""

PIDSTORE_EXTRA_DNB_SANDBOX_URI = "https://api.nbn-resolving.org/sandbox/v2/"
"""In case the sandbox is not available this setting allows configuration of a different URI."""

PIDSTORE_EXTRA_FORMAT = "{prefix}-{id}"
"""The format of the URN."""
