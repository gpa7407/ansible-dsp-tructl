#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: key_provider
short_description: Manage DSP key management providers
version_added: "1.0.0"
description:
- Creates, deletes, or lists key management providers in the DSP platform.
- Key providers configure external key management systems (e.g., HSMs, cloud KMS) used by the KAS.
- This module is idempotent when O(state=present) and checks for existing providers by O(name).
options:
  name:
    description:
    - The key provider name.
    - Required when O(state=present).
    type: str
  manager:
    description:
    - The key manager type or identifier.
    - Required when O(state=present).
    type: str
  config:
    description:
    - Optional configuration dictionary passed as JSON to the tructl CLI.
    type: dict
  id:
    description:
    - The key provider ID.
    - Required when O(state=absent) to identify the provider to delete.
    type: str
  state:
    description:
    - V(present) creates the key provider if one does not exist with the given O(name).
    - V(absent) deletes the key provider identified by O(id).
    - V(list) returns all key providers.
    choices: [present, absent, list]
    default: present
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- This module requires C(tructl) to be installed on the Ansible controller.
- Check mode is supported for all states.
seealso:
- module: virtru.dsp_tructl.kas_registry
- module: virtru.dsp_tructl.kas_key
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
- Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Create a key provider
  virtru.dsp_tructl.key_provider:
    name: primary-hsm
    manager: local
    state: present

- name: Create a key provider with config
  virtru.dsp_tructl.key_provider:
    name: cloud-kms
    manager: aws-kms
    config:
      region: us-east-1
      key_arn: "arn:aws:kms:us-east-1:123456789:key/abc-123"
    state: present

- name: List all key providers
  virtru.dsp_tructl.key_provider:
    state: list
  register: kp_result

- name: Delete a key provider by ID
  virtru.dsp_tructl.key_provider:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
key_provider:
    description: The key provider details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "name": "primary-hsm", "manager": "local"}
key_providers:
    description: List of all key providers.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "name": "primary-hsm", "manager": "local"}]
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
        manager=dict(type='str'),
        config=dict(type='dict'),
        id=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['name', 'manager']),
            ('state', 'absent', ['id']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    result = dict(changed=False)

    # List current key providers
    existing = runner.list_resources(['policy', 'keymanagement', 'provider'])

    if state == 'list':
        result['key_providers'] = existing
        module.exit_json(**result)

    if state == 'present':
        name = module.params['name']
        current = runner.find_by_field(existing, 'name', name)

        if current:
            result['key_provider'] = current
            module.exit_json(**result)

        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        args = ['policy', 'keymanagement', 'provider', 'create',
                '--name', name, '--manager', module.params['manager']]
        if module.params.get('config'):
            args.extend(['--config', json.dumps(module.params['config'])])
        args.append('--json')
        output = runner.run_command(args, parse_json=True)
        result['changed'] = True
        result['key_provider'] = output

    elif state == 'absent':
        provider_id = module.params['id']
        current = runner.find_by_field(existing, 'id', provider_id)
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(
                ['policy', 'keymanagement', 'provider', 'delete', '--id', provider_id, '--force']
            )
            result['changed'] = True
            result['key_provider'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
