# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# invenio-pidstore-extra is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


# Usage:
#   ./run-tests.sh [pytest options and args...]
#
# Example for additional output:
#   ./run-tests.sh -vv

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Manifest check
# python -m check_manifest

# Pytests
python -m pytest ${pytest_args[@]+"${pytest_args[@]}"}
tests_exit_code=$?
exit "$tests_exit_code"
