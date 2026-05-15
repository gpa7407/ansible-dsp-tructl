#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: policy_export
short_description: Export policy configuration using tructl
version_added: "1.1.0"
description:
- Exports policy configuration from the platform to a local file using C(tructl export).
- The exported bundle can later be imported into another environment with M(dsp.tructl.policy_import).
- This module is idempotent by default and skips the export if the destination file already exists.
  Use O(force=true) to overwrite an existing file.
options:
  namespace:
    description:
    - The policy namespace to export.
    required: yes
    type: str
  dest:
    description:
    - Output file path for the exported policy bundle.
    required: yes
    type: str
  no_bundle:
    description:
    - If set to V(true), export raw policy data instead of a signed bundle.
    type: bool
    default: false
  force:
    description:
    - If set to V(true), overwrite the destination file even if it already exists.
    - If set to V(false), the module will skip the export when the destination exists.
    type: bool
    default: false
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
  host:
    description:
    - Platform endpoint URL.
    type: str
  tls_no_verify:
    description:
    - If set to V(true), skip TLS certificate verification.
    type: bool
    default: false
  client_creds:
    description:
    - Dictionary with C(clientId) and C(clientSecret) for authentication.
    type: dict
notes:
- Authentication must be configured via O(client_creds) or a prior M(dsp.tructl.auth) call.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: dsp.tructl.policy_import
- module: dsp.tructl.provision
- module: dsp.tructl.auth
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Export policy for a namespace
  dsp.tructl.policy_export:
    namespace: demo.com
    dest: /tmp/demo-policy.bundle
    host: https://platform.dsp.vm
    client_creds:
      clientId: opentdf
      clientSecret: secret

- name: Export raw policy data (no bundle)
  dsp.tructl.policy_export:
    namespace: demo.com
    dest: /tmp/demo-policy.json
    no_bundle: true

- name: Force re-export of an existing file
  dsp.tructl.policy_export:
    namespace: demo.com
    dest: /tmp/demo-policy.bundle
    force: true
"""

RETURN = r"""
dest:
    description: Path to the exported policy file.
    returned: success
    type: str
    sample: "/tmp/demo-policy.bundle"
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dsp.tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        namespace=dict(type='str', required=True),
        dest=dict(type='str', required=True),
        no_bundle=dict(type='bool', default=False),
        force=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    dest = module.params['dest']
    force = module.params['force']
    result = dict(changed=False, dest=dest)

    if os.path.isfile(dest) and not force:
        module.exit_json(**result)

    if module.check_mode:
        result['changed'] = True
        module.exit_json(**result)

    runner = TructlRunner(module)

    args = ['export', '--namespace', module.params['namespace'], '--out', dest]
    if module.params['no_bundle']:
        args.append('--no-bundle')

    runner.run_command(args)
    result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
