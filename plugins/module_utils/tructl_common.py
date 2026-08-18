#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared helper utilities for tructl Ansible modules."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import re

_UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


def is_uuid(value):
    """Return True if value looks like a UUID."""
    return bool(value) and bool(_UUID_RE.match(str(value)))


def common_argument_spec():
    """Return argument spec shared by all tructl modules."""
    return dict(
        tructl_bin=dict(type='str', default='tructl'),
        host=dict(type='str'),
        tls_no_verify=dict(type='bool', default=False),
        client_creds=dict(type='dict', no_log=True),
    )


def state_argument_spec():
    """Return argument spec for state-based modules."""
    spec = common_argument_spec()
    spec['state'] = dict(type='str', default='present', choices=['present', 'absent', 'list'])
    return spec


class TructlRunner:
    """Helper class for executing tructl CLI commands via Ansible module.run_command()."""

    def __init__(self, module):
        self.module = module
        self.tructl_bin = module.params.get('tructl_bin', 'tructl')
        self.global_flags = self._build_global_flags()

    def _build_global_flags(self):
        """Build global CLI flags from module params."""
        flags = []
        if self.module.params.get('host'):
            flags.extend(['--host', self.module.params['host']])
        if self.module.params.get('tls_no_verify'):
            flags.append('--tls-no-verify')
        if self.module.params.get('client_creds'):
            flags.extend(['--with-client-creds', json.dumps(self.module.params['client_creds'])])
        return flags

    def run_command(self, args, check_rc=True, parse_json=False):
        """Execute a tructl command.

        Args:
            args: List of command arguments (without the tructl binary).
            check_rc: If True, fail the module on non-zero return code.
            parse_json: If True, parse stdout as JSON.

        Returns:
            Parsed JSON (dict/list) if parse_json=True, otherwise raw stdout string.
        """
        cmd = [self.tructl_bin] + self.global_flags + args
        rc, stdout, stderr = self.module.run_command(cmd)

        if check_rc and rc != 0:
            self.module.fail_json(
                msg="tructl command failed",
                cmd=' '.join(cmd),
                rc=rc,
                stdout=stdout,
                stderr=stderr,
            )

        if parse_json and stdout.strip():
            try:
                return json.loads(stdout)
            except (json.JSONDecodeError, ValueError):
                self.module.fail_json(
                    msg="Failed to parse tructl JSON output",
                    cmd=' '.join(cmd),
                    stdout=stdout,
                    stderr=stderr,
                )

        if parse_json:
            return []

        return stdout

    def list_resources(self, subcommand_args):
        """Run a tructl list command with --json and return parsed result.

        Args:
            subcommand_args: List of args before 'list' (e.g., ['policy', 'attributes', 'namespaces']).

        Returns:
            List of resource dicts.
        """
        args = subcommand_args + ['list', '--json']
        result = self.run_command(args, parse_json=True)
        if isinstance(result, dict):
            # Some tructl commands wrap the list in a key
            for key in result:
                if isinstance(result[key], list):
                    return result[key]
            return [result]
        return result if isinstance(result, list) else []

    def resolve_namespace_id(self, namespace):
        """Resolve a namespace to its UUID.

        DSP 2.0.7's tructl requires namespace references as UUIDs where earlier
        versions accepted the name/FQN. Accepts a UUID (returned as-is), a name
        (e.g. C(example.com)), or an FQN (e.g. C(https://example.com)).
        """
        if is_uuid(namespace):
            return namespace
        namespaces = self.list_resources(['policy', 'attributes', 'namespaces'])
        for ns in namespaces:
            if namespace in (ns.get('name'), ns.get('fqn')):
                return ns.get('id')
        self.module.fail_json(
            msg="Could not resolve namespace '{0}' to an ID".format(namespace),
            available=[ns.get('name') or ns.get('fqn') for ns in namespaces],
        )

    def find_by_field(self, items, field, value):
        """Find a resource in a list by matching a field value.

        Args:
            items: List of resource dicts.
            field: Field name to match on.
            value: Value to match.

        Returns:
            Matching dict or None.
        """
        if not items:
            return None
        for item in items:
            if item.get(field) == value:
                return item
        return None
