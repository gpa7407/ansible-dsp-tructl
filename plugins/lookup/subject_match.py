# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
name: subject_match
author: Virtru (@virtru)
version_added: "1.0.0"
short_description: Look up subject mapping matches via tructl
description:
- Runs C(tructl policy subject-mappings match) to resolve which subject mappings apply
  to one or more subject entity JSON descriptions.
- Returns the parsed JSON output from tructl as a list of matched subject mappings.
options:
  _terms:
    description:
    - One or more subject entity JSON strings to match against platform policy.
    - Each term is passed as the C(--subject) argument to tructl.
    required: true
    type: list
    elements: str
  host:
    description:
    - Platform endpoint URL.
    type: str
    required: false
  tls_no_verify:
    description:
    - If set to V(true), skip TLS certificate verification.
    type: bool
    default: false
  client_creds:
    description:
    - Dictionary with C(clientId) and C(clientSecret) for authentication.
    type: dict
    required: false
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
  selectors:
    description:
    - List of selector expressions to narrow the match.
    - Each selector is passed as a separate C(--selector) flag.
    type: list
    elements: str
    required: false
notes:
- This lookup plugin runs tructl via C(subprocess) on the Ansible controller.
- Authentication must be configured via O(client_creds) or a prior C(tructl auth) profile.
- The plugin requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: virtru.dsp_tructl.subject_mapping
- module: virtru.dsp_tructl.auth
"""

EXAMPLES = r"""
- name: Check entitlements for a subject
  ansible.builtin.debug:
    msg: "{{ lookup('virtru.dsp_tructl.subject_match', '{\"sub\": \"user1\"}', host='https://platform.dsp.vm', tls_no_verify=true, client_creds={'clientId': 'opentdf', 'clientSecret': 'secret'}) }}"

- name: Match with selectors
  ansible.builtin.debug:
    msg: "{{ lookup('virtru.dsp_tructl.subject_match', '{\"sub\": \"user1\"}', host='https://platform.dsp.vm', selectors=['.department', '.title'], client_creds={'clientId': 'opentdf', 'clientSecret': 'secret'}) }}"

- name: Match multiple subjects
  ansible.builtin.debug:
    msg: "{{ lookup('virtru.dsp_tructl.subject_match', '{\"sub\": \"user1\"}', '{\"sub\": \"user2\"}', host='https://platform.dsp.vm', client_creds={'clientId': 'opentdf', 'clientSecret': 'secret'}) }}"

- name: Store result in a variable
  ansible.builtin.set_fact:
    entitlements: "{{ lookup('virtru.dsp_tructl.subject_match', subject_json, host=platform_host, client_creds=creds) }}"
"""

RETURN = r"""
_raw:
    description:
    - List of matched subject mapping objects returned by tructl.
    - Each element corresponds to the match result for one input subject term.
    type: list
    elements: dict
"""

import json
import subprocess

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        tructl_bin = self.get_option('tructl_bin') or 'tructl'
        host = self.get_option('host')
        tls_no_verify = self.get_option('tls_no_verify')
        client_creds = self.get_option('client_creds')
        selectors = self.get_option('selectors')

        global_flags = []
        if host:
            global_flags.extend(['--host', host])
        if tls_no_verify:
            global_flags.append('--tls-no-verify')
        if client_creds:
            global_flags.extend(['--with-client-creds', json.dumps(client_creds)])

        results = []

        for term in terms:
            cmd = [tructl_bin] + global_flags + [
                'policy', 'subject-mappings', 'match',
                '--subject', term,
            ]
            if selectors:
                for sel in selectors:
                    cmd.extend(['--selector', sel])
            cmd.append('--json')

            display.vvvv("subject_match lookup running: %s" % ' '.join(cmd))

            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError:
                raise AnsibleError("tructl binary not found: %s" % tructl_bin)
            except OSError as e:
                raise AnsibleError("Failed to execute tructl: %s" % str(e))

            if proc.returncode != 0:
                raise AnsibleError(
                    "tructl command failed (rc=%d): %s\nstderr: %s"
                    % (proc.returncode, ' '.join(cmd), proc.stderr)
                )

            stdout = proc.stdout.strip()
            if not stdout:
                results.append([])
                continue

            try:
                parsed = json.loads(stdout)
            except (json.JSONDecodeError, ValueError) as e:
                raise AnsibleError(
                    "Failed to parse tructl JSON output: %s\nOutput: %s"
                    % (str(e), stdout)
                )

            if isinstance(parsed, list):
                results.append(parsed)
            else:
                results.append([parsed])

        return results
