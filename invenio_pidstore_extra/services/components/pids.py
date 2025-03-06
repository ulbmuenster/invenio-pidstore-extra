# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Extra RDM service component for RRN relations."""

from copy import copy

from invenio_drafts_resources.services.records.components import ServiceComponent


class URNRelationsComponent(ServiceComponent):
    """Service component for URN relations."""

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        # Extract all current PIDs/schemes from the parent record. These are coming from
        # previously published record versions.
        current_pids = copy(record.parent.get("pids", {}))
        current_schemes = set(current_pids.keys())
        required_schemes = set(self.service.config.parent_pids_required)
