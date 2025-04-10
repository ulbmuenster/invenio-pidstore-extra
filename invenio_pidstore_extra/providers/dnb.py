# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""DNB urn client and provider to use the dnb-urn-service API wrapper."""

import json

from flask import current_app
from invenio_pidstore.models import PIDStatus
from invenio_rdm_records.services.pids.providers import PIDProvider
from invenio_rdm_records.utils import ChainObject

from .urn import DNBURNServiceError, DNBUrnServiceRESTClient


class DNBUrnClient:
    """DNB Urn Client."""

    def __init__(
        self,
        name,
        prefix=None,
        username=None,
        password=None,
        urn_format=None,
        test_mode=True,
        **kwargs,
    ):
        """Constructor."""
        self.name = name
        self._prefix = prefix
        self._username = username
        self._password = password
        self._urn_format = urn_format
        self._test_mode = test_mode
        if not (
            self._prefix and self._username and self._password and self._urn_format
        ):
            message = (
                f"The {self.__class__.__name__} is misconfigured. Please "
                f"set PIDSTORE_EXTRA_DNB_USERNAME, PIDSTORE_EXTRA_DNB_PASSWORD, "
                f"PIDSTORE_EXTRA_FORMAT and PIDSTORE_EXTRA_DNB_ID_PREFIX in your configuration."
            )
            raise RuntimeError(message)
        self._api = None

    def generate_urn(self, record):
        """Generate a URN."""
        return self._urn_format.format(prefix=self._prefix, id=record.pid.pid_value)

    @property
    def api(self):
        """DNB URN Service API client instance."""
        if self._api is None:
            self._api = DNBUrnServiceRESTClient(
                self._username,
                self._password,
                self._prefix,
                self._test_mode,
            )
        return self._api


class DnbUrnProvider(PIDProvider):
    """DNB Provider class.

    The DNB is only contacted when a URN is reserved or
    registered, or any action posterior to it. Its creation happens
    only at PIDStore level.
    """

    def __init__(
        self,
        id_,
        client=None,
        serializer=None,
        pid_type="urn",
        default_status=PIDStatus.NEW,
        **kwargs,
    ):
        """Constructor."""
        super().__init__(
            id_,
            client=(client or DNBUrnClient("dnb")),
            pid_type=pid_type,
            default_status=default_status,
        )

    @classmethod
    def is_enabled(cls, app):
        """Determine if the pid is enabled or not."""
        return app.config.get("PIDSTORE_EXTRA_DNB_ENABLED")

    @staticmethod
    def _log_errors(errors):
        """Log errors from DNBURNServiceError class."""
        # DNBURNServiceError is a tuple with the errors on the first
        errors = json.loads(errors.args[0])["errors"]
        for error in errors:
            field = error["source"]
            reason = error["title"]
            current_app.logger.error(f"Error in {field}: {reason}")

    def generate_id(self, record, **kwargs):
        """Generate a unique URN."""
        # Delegate to client
        return self.client.generate_urn(record)

    def can_modify(self, pid, **kwargs):
        """Checks if the PID can be modified."""
        return not pid.is_registered() and not pid.is_reserved()

    def register(self, pid, record, **kwargs):
        """Register a URN via the DNB URN service API.

        :param pid: the PID to register.
        :param record: the record metadata for the URN.
        :returns: `True` if is registered successfully.
        """
        if isinstance(record, ChainObject):
            if record._child["access"]["record"] == "restricted":
                return False
        elif record["access"]["record"] == "restricted":
            return False

        local_success = super().register(pid)
        if not local_success:
            return False

        try:
            url = kwargs["url"]
            self.client.api.create_urn(url=url, urn=pid.pid_value)
            return True
        except DNBURNServiceError as e:
            current_app.logger.warning(
                "URN provider error when " f"registering URN for {pid.pid_value}"
            )
            self._log_errors(e)
            return False

    def update(self, pid, record, url=None, **kwargs):
        """Update url associated with a URN.

        This can be called after a URN is registered.
        :param pid: the PID to register.
        :param record: the record metadata for the URN.
        :param url: the URL associated with the URN.
        :returns: `True` if is updated successfully.
        """
        hide = False
        if isinstance(record, ChainObject):
            if record._child["access"]["record"] == "restricted":
                hide = True
        elif record["access"]["record"] == "restricted":
            hide = True
        if hide:
            current_app.logger.warning(
                f"Hiding or deleting URN's is not allowed for {pid.pid_value}"
            )

            return False

        try:
            self.client.api.modify_urn(urn=pid.pid_value, url=url)
        except DNBURNServiceError as e:
            current_app.logger.warning(
                f"URN provider error when updating URL for {pid.pid_value}"
            )
            self._log_errors(e)

            return False

        if pid.is_deleted():
            return pid.sync_status(PIDStatus.REGISTERED)

        return True

    def delete(self, pid, **kwargs):
        """Delete/unregister a registered URN.

        If the PID has not been reserved then it's deleted only locally.
        Otherwise, there is a problem: a URN can't be deleted remotely.
        :returns: `True` if is deleted successfully.
        """
        return super().delete(pid, **kwargs)

    def validate(self, record, identifier=None, provider=None, **kwargs):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). The first specifies if the
                  validation was passed successfully. The second one is an
                  array of error messages.
        """
        success, errors = super().validate(record, identifier, provider, **kwargs)

        # Format check
        if identifier is not None:
            try:
                self.client.api.check_urn(identifier)
            except ValueError as e:
                errors.append(str(e))

        return not bool(errors), errors
