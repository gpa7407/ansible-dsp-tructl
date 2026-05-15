#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: provision
short_description: Provision policy configuration using tructl
version_added: "1.1.0"
description:
- Provisions policy configuration on the platform using C(tructl provision policy).
- This is typically used to seed a new environment with default namespaces, attributes,
  subject mappings, resource mappings, and obligations.
- This module always reports C(changed=true) because provisioning is not idempotent.
options:
  namespace:
    description:
    - The namespace to provision.
    type: str
    default: demo.com
  file:
    description:
    - Path to a custom provisioning configuration file.
    - When specified, tructl uses this file instead of built-in defaults.
    type: str
  with_resource_mappings:
    description:
    - If set to V(true), include resource mappings in the provisioning.
    type: bool
    default: true
  with_subject_mappings:
    description:
    - If set to V(true), include subject mappings in the provisioning.
    type: bool
    default: true
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
- This module always reports C(changed=true) because provisioning is not idempotent.
- Authentication must be configured via O(client_creds) or a prior M(dsp.tructl.auth) call.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: dsp.tructl.policy_export
- module: dsp.tructl.policy_import
- module: dsp.tructl.auth
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Provision demo namespace with defaults
  dsp.tructl.provision:
    host: https://platform.dsp.vm
    client_creds:
      clientId: opentdf
      clientSecret: secret

- name: Provision a custom namespace
  dsp.tructl.provision:
    namespace: acme.com
    host: https://platform.dsp.vm
    client_creds:
      clientId: opentdf
      clientSecret: secret

- name: Provision from a custom configuration file
  dsp.tructl.provision:
    file: /opt/dsp/policy-config.yaml
    host: https://platform.dsp.vm
    client_creds:
      clientId: opentdf
      clientSecret: secret

- name: Provision without resource or subject mappings
  dsp.tructl.provision:
    namespace: demo.com
    with_resource_mappings: false
    with_subject_mappings: false
    host: https://platform.dsp.vm
    client_creds:
      clientId: opentdf
      clientSecret: secret

"""

RETURN = r"""
stdout:
    description: Standard output from the tructl provision command.
    returned: success
    type: str
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dsp.tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        namespace=dict(type='str', default='demo.com'),
        file=dict(type='str'),
        with_resource_mappings=dict(type='bool', default=True),
        with_subject_mappings=dict(type='bool', default=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = dict(changed=False)

    if module.params.get('file') and not os.path.isfile(module.params['file']):
        module.fail_json(msg="Provisioning file does not exist: %s" % module.params['file'])

    if module.check_mode:
        result['changed'] = True
        module.exit_json(**result)

    runner = TructlRunner(module)

    args = ['provision', 'policy']
    if module.params.get('namespace'):
        args.extend(['--namespace', module.params['namespace']])
    if module.params.get('file'):
        args.extend(['--file', module.params['file']])
    if module.params['with_resource_mappings']:
        args.append('--with-resource-mappings')
    if module.params['with_subject_mappings']:
        args.append('--with-subject-mappings')

    stdout = runner.run_command(args)
    result['changed'] = True
    result['stdout'] = stdout

    module.exit_json(**result)


if __name__ == '__main__':
    main()
