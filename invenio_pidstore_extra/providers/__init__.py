# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""URN providers."""


from .dnb import DNBUrnClient, DnbUrnProvider

__all__ = (DNBUrnClient, DnbUrnProvider)
