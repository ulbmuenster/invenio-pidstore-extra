..
    Copyright (C) 2024-2025 University of Münster.

    invenio-pidstore-extra is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

======================
 invenio-pidstore-extra
======================

Module that adds URN minting by DNB epicur service.

InvenioRDM supports DOI minting with Datacite out of the box. This module adds support for UTRN minting by using the URN API published by German National Library (DNB).
The flask app `invenio_pidstore_extra.dnb-sandbox.py` contains a very simple implementation of the DNB api to allow testing the URN support when the DNB sandbox is not available or just no user has been provided. You can start it with calling

.. raw::
   flask --app invenio_pidstore_extra.dnb-sandbox run --port=8000



