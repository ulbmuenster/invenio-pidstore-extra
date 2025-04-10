# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module that adds URN minting by DNB epicur service."""

from .ext import InvenioUrnProvider

__version__ = "0.2.0"

__all__ = ("__version__", "InvenioUrnProvider")
