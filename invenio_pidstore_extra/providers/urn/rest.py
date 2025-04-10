# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 University Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Python API client wrapper for the DNB URN service API.

API documentation is available at
https://wiki.dnb.de/display/URNSERVDOK/URN-Service+API.
"""

import json
from urllib.parse import urljoin

import requests
from flask import current_app
from idutils.normalizers import normalize_urn

from .errors import DNBURNServiceError, DNBURNServiceUserNotAuthorizedError
from .request import DNBUrnServiceRequest

HTTP_OK = requests.codes["ok"]
HTTP_CREATED = requests.codes["created"]
HTTP_NO_CONTENT = requests.codes["no_content"]


class DNBUrnServiceRESTClient(object):
    """DNB URN service API client wrapper."""

    def __init__(
        self, username, password, prefix, test_mode=False, url=None, timeout=None
    ):
        """Initialize the API client wrapper.

        :param username: DNB username.
        :param password: DNB password.
        :param prefix: URN prefix (or DNB_URN_PREFIX).
        :param test_mode: use test URL when True
        :param url: DNB URN service API base URL.
        :param timeout: Connect and read timeout in seconds. Specify a tuple
            (connect, read) to specify each timeout individually.
        """
        self.username = str(username)
        self.password = str(password)
        self.prefix = str(prefix)

        if test_mode:
            self.api_url = current_app.config.get("PIDSTORE_EXTRA_DNB_SANDBOX_URI")
        else:
            self.api_url = url or "https://api.nbn-resolving.org/v2/"

        if not self.api_url.endswith("/"):
            self.api_url += "/"

        self.timeout = timeout

    def __repr__(self):
        """Create string representation of object."""
        return "<DNBUrnServiceRESTClient: {0}>".format(self.username)

    def _create_request(self):
        """Create a new Request object."""
        return DNBUrnServiceRequest(
            base_url=self.api_url,
            username=self.username,
            password=self.password,
            timeout=self.timeout,
        )

    def get_urn(self, urn):
        """Get the URL where the resource pointed by the URN is located.

        :param urn: URN name of the resource.
        """
        request = self._create_request()
        resp = request.get("urns/urn/" + urn + "/my-urls")
        if resp.status_code == HTTP_OK:
            return resp.json()["items"][0]["url"]
        else:
            raise DNBURNServiceError.factory(resp.status_code, resp.text)

    def head_urn(self, urn):
        """Check if a URN is registered.

        :param urn: URN name of the resource.
        """
        request = self._create_request()
        resp = request.head("urns/urn/" + urn)
        if resp.status_code == HTTP_OK:
            return normalize_urn(urn)
        else:
            raise DNBURNServiceError.factory(resp.status_code, resp.text)

    def check_urn(self, urn):
        """Check urn structure.

        Check that the urn has a form
        urn:nbn: with the prefix defined
        """
        split = urn.split("-")
        prefix = split[0] + "-"
        if not urn.startswith(self.prefix):
            # Provided a URN with the wrong prefix
            raise ValueError(
                "Wrong URN {0} prefix provided, it should be "
                "{1} as defined in the rest client".format(prefix, self.prefix)
            )
        return normalize_urn(urn)

    def post_urn(self, data):
        """Post a new JSON payload to DNB."""
        headers = {
            "content-type": "application/json",
            "accept": "application/json",
        }
        request = self._create_request()
        response = request.post("urns", body=json.dumps(data), headers=headers)
        if response.status_code == HTTP_CREATED:
            return normalize_urn(response.json()["urn"])
        else:
            raise DNBURNServiceError.factory(response.status_code, response.text)

    def patch_urn(self, urn, data):
        """Patch a new JSON payload to DNB."""
        headers = {"content-type": "application/json"}
        request = self._create_request()
        response = request.patch(
            "urns/urn/" + urn, body=json.dumps(data), headers=headers
        )
        if response.status_code == HTTP_NO_CONTENT:
            return ""
        else:
            raise DNBURNServiceError.factory(response.status_code, response.text)

    def patch_urls(self, urn, data):
        """Patch a new JSON payload to patch the URL's at DNB."""
        headers = {"content-type": "application/json"}
        request = self._create_request()
        resp = request.patch(
            "urns/urn/" + urn + "/my-urls", body=json.dumps(data), headers=headers
        )
        if resp.status_code == HTTP_NO_CONTENT:
            return ""
        else:
            raise DNBURNServiceError.factory(resp.status_code, resp.text)

    def delete_urn(self, urn):
        """Delete a URN completely.

        As this action is only allowed for system administrators
        directly raise a DNBURNServiceUserNotAuthorizedError
        """
        raise DNBURNServiceUserNotAuthorizedError

    def create_urn(self, url, urn):
        """Create an urn.

        This URN will be public and can be deleted.
        If urn is not provided, there will be an error.
        :param url: URL where the urn will resolve.
        :param urn: URN (e.g. urn:nbn:de:hbz:6-1234)
        :return:
        """
        data = {"urn": urn, "urls": [{"url": url, "priority": 10}]}
        return self.post_urn(data)

    def modify_urn(self, url, urn):
        """Modify the url of an existing urn.

        This URN will be public and can't be deleted.
        If urn is not provided, there will be an error.
        :param url: URL where the urn will resolve.
        :param urn: URN (e.g. urn:nbn:de:hbz:6-1234)
        :return:
        """
        data = {[{"url": url, "priority": 10}]}
        return self.patch_urls(urn, data)

    def check_if_registered(self, urn):
        """Check if a URN is registered."""
        return self.head_urn(urn)

    def create_successor(self, urn, successor):
        """Set a successor urn."""
        data = {"successor": urljoin(self.api_url, "urns/urn/" + successor)}

        return self.patch_urn(urn, data)

    def remove_successor(self, urn):
        """Set a successor urn."""
        data = {"successor": None}

        return self.patch_urn(urn, data)
