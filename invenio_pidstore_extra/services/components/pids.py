# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Extra RDM service component for RRN relations."""

import collections
import sys

from invenio_drafts_resources.services.records.components import ServiceComponent


def set_urn_forwarding(siblings, deleted, service):
    """Apply the urn-forwarding to the given URN's."""
    sorted_siblings = collections.OrderedDict(sorted(siblings.items()))
    sorted_deleted = collections.OrderedDict(sorted(deleted.items()))

    first_siblings_id = (
        next(iter(sorted_siblings)) if len(siblings) > 0 else sys.maxsize
    )
    first_deleted_id = next(iter(sorted_deleted)) if len(deleted) > 0 else sys.maxsize
    first_id = min(first_siblings_id, first_deleted_id)
    latest_id = (
        list(sorted_siblings.keys())[-1]
        if len(list(sorted_siblings.keys())) > 0
        else None
    )
    if first_siblings_id in siblings:
        first_sibling = siblings[first_id]
    elif first_deleted_id in deleted:
        first_sibling = deleted[first_id]
    else:
        first_sibling = None
    if first_sibling:
        sibling_pids = first_sibling.get("pids", {})
        sibling_schemes = set(sibling_pids.keys())
        if "urn" in sibling_schemes:
            if latest_id is None:
                # Remove forwarding of URN
                service.pids.pid_manager._get_provider(
                    "urn", "urn"
                ).client.api.remove_successor(sibling_pids["urn"]["identifier"])
            else:
                newest_sibling_pids = siblings[latest_id].get("pids", {})
                if (
                    sibling_pids["urn"]["identifier"]
                    == newest_sibling_pids["urn"]["identifier"]
                ):
                    service.pids.pid_manager._get_provider(
                        "urn", "urn"
                    ).client.api.remove_successor(sibling_pids["urn"]["identifier"])
                else:
                    service.pids.pid_manager._get_provider(
                        "urn", "urn"
                    ).client.api.create_successor(
                        sibling_pids["urn"]["identifier"],
                        newest_sibling_pids["urn"]["identifier"],
                    )
                # Forward URN's


class URNRelationsComponent(ServiceComponent):
    """Service component for URN relations."""

    def publish(self, identity, draft=None, record=None):
        """Set the successor urn when a new version is published."""
        new_id = record.get("pid")["pk"]
        sibling_records = self.service.record_cls.get_records_by_parent(
            parent=record.parent
        )
        siblings = {new_id: record}
        deleted = {}
        for sibling in sibling_records:
            if sibling is not None and sibling.get("pid") is not None:
                sibling_id = sibling.get("pid")["pk"]
                if "tombstone" in sibling.keys():
                    deleted[sibling_id] = sibling
                else:
                    siblings[sibling_id] = sibling

        set_urn_forwarding(siblings, deleted, self.service)

    def delete_record(self, identity, data=None, record=None, uow=None):
        """Process pids on delete record."""
        deleted_id = record.get("pid")["pk"]
        sibling_records = self.service.record_cls.get_records_by_parent(
            parent=record.parent
        )
        siblings = {}
        deleted = {}
        for sibling in sibling_records:
            if sibling is not None:
                sibling_id = sibling.get("pid")["pk"]
                if "tombstone" in sibling.keys() or sibling_id == deleted_id:
                    deleted[sibling_id] = sibling
                else:
                    siblings[sibling_id] = sibling

        set_urn_forwarding(siblings, deleted, self.service)

    def restore_record(self, identity, record=None, uow=None):
        """Restore previously invalidated pids."""
        restored_id = record.get("pid")["pk"]
        sibling_records = self.service.record_cls.get_records_by_parent(
            parent=record.parent
        )
        siblings = {restored_id: record}
        deleted = {}
        for sibling in sibling_records:
            if sibling is not None:
                sibling_id = sibling.get("pid")["pk"]
                if "tombstone" in sibling.keys() and not sibling_id == restored_id:
                    deleted[sibling_id] = sibling
                else:
                    siblings[sibling_id] = sibling

        set_urn_forwarding(siblings, deleted, self.service)
