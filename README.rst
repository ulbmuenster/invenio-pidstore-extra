..
    Copyright (C) 2024-2025 University of Münster.

    invenio-pidstore-extra is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

=======================
 invenio-pidstore-extra
=======================

Module that adds URN minting by DNB epicur service.

InvenioRDM supports DOI minting with Datacite out of the box. This module adds support for URN minting by using the
URN API published by German National Library (DNB).

Configuration
=============

After adding the module to your InvenioRDM instance you need to add the following snippet to your `invenio.cfg`.
Make sure you have registered at the DNB and set the config variables below to the correct values!

When putting this to production, set `PIDSTORE_EXTRA_TEST_MODE = False`!

.. code-block:: python

    PIDSTORE_EXTRA_DNB_SANDBOX_URI = "http://127.0.0.1:8000/"

    PIDSTORE_EXTRA_DNB_ENABLED = True
    PIDSTORE_EXTRA_DNB_USERNAME = "username"
    PIDSTORE_EXTRA_DNB_PASSWORD = "password"
    PIDSTORE_EXTRA_DNB_ID_PREFIX = "urn:nbn:de:hbz:6"
    PIDSTORE_EXTRA_FORMAT = "{prefix}-{id}"
    PIDSTORE_EXTRA_TEST_MODE = True

    #
    # Persistent identifiers configuration
    #
    from invenio_rdm_records.config import RDM_PERSISTENT_IDENTIFIER_PROVIDERS as DEFAULT_PERSISTENT_IDENTIFIER_PROVIDERS
    from invenio_pidstore_extra import providers

    RDM_PERSISTENT_IDENTIFIER_PROVIDERS = DEFAULT_PERSISTENT_IDENTIFIER_PROVIDERS + [
        providers.DnbUrnProvider(
          "urn",
          client=providers.DNBUrnClient("dnb", PIDSTORE_EXTRA_DNB_ID_PREFIX, PIDSTORE_EXTRA_DNB_USERNAME, PIDSTORE_EXTRA_DNB_PASSWORD, PIDSTORE_EXTRA_FORMAT),
          label=_("URN"),
        ),
    ]

    from invenio_rdm_records.config import RDM_PERSISTENT_IDENTIFIERS as DEFAULT_PERSISTENT_IDENTIFIERS

    RDM_PERSISTENT_IDENTIFIERS = {
        **DEFAULT_PERSISTENT_IDENTIFIERS,
        "urn": {
          "providers": ["urn"],
          "required": True,
          "label": _("URN"),
          "is_enabled": providers.DnbUrnProvider.is_enabled,
        },
    }

    from invenio_pidstore_extra.services.components import URNRelationsComponent
    from invenio_rdm_records.services.components import DefaultRecordsComponents

    RDM_RECORDS_SERVICE_COMPONENTS = DefaultRecordsComponents + [URNRelationsComponent]

Development
===========

The flask app `invenio_pidstore_extra.dnb-sandbox.py` contains a very simple implementation of the DNB api to allow testing the URN support when the DNB sandbox is not available or just no user has been provided. You can start it with calling

.. code-block:: console

   flask --app invenio_pidstore_extra.dnb-sandbox run --port=8000

