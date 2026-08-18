#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    """Common connection options shared by the tructl modules."""

    DOCUMENTATION = r"""
options:
  host:
    description:
    - The DSP platform endpoint URL (for example V(https://platform.dsp.vm)).
    type: str
  tls_no_verify:
    description:
    - If V(true), skip verification of the platform's TLS certificate.
    type: bool
    default: false
  client_creds:
    description:
    - Client credentials used to authenticate to the platform, as a dict containing
      C(clientId) and C(clientSecret) (and optionally C(scopes)).
    type: dict
"""
