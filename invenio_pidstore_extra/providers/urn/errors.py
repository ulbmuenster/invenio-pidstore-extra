# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 University Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Errors for the DNB URN service API."""


class HttpError(Exception):
    """Exception raised when a connection problem happens."""


class DNBURNServiceError(Exception):
    """Exception raised when the server returns a known HTTP error code."""

    @staticmethod
    def factory(err_code, *args):
        """Create exceptions through a Factory based on the HTTP error code."""
        if err_code == 400:
            return DNBURNServiceNotValidError
        if err_code == 401:
            return DNBURNServiceUserNotAuthenticatedError
        if err_code == 403:
            return DNBURNServiceUserNotAuthorizedError
        if err_code == 404:
            return DNBURNServiceUrnNotRegisteredError
        if err_code == 409:
            return DNBURNServiceConflictError
        else:
            return DNBURNServiceServerError


class DNBURNServiceServerError(DNBURNServiceError):
    """An internal server error happened on the DNB end. Try later.

    Base class for all 5XX-related HTTP error codes.
    """


class DNBURNServiceNotValidError(DNBURNServiceError):
    """The information is not valid.

    Base class for 400-related HTTP error code.
    """


class DNBURNServiceUserNotAuthenticatedError(DNBURNServiceError):
    """The user is not authenticated.

    Base class for 401-related HTTP error code.
    """


class DNBURNServiceUserNotAuthorizedError(DNBURNServiceError):
    """The user is not authorized.

    Base class for 403-related HTTP error code.
    """


class DNBURNServiceUrnNotRegisteredError(DNBURNServiceError):
    """The requested URN is not registered.

    Base class for 404-related HTTP error code.
    """


class DNBURNServiceConflictError(DNBURNServiceError):
    """The requested URN is already registered.

    Base class for 409-related HTTP error code.
    """
