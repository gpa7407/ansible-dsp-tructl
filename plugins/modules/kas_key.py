#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: kas_key
short_description: Manage KAS registry keys
version_added: "1.0.0"
description:
- Imports keys or sets base keys for Key Access Server (KAS) registry entries.
- Key operations are essential for enabling encryption and decryption through the KAS.
options:
  kas_id:
    description:
    - The KAS registry entry ID to manage keys for.
    required: yes
    type: str
  action:
    description:
    - The key operation to perform.
    - V(import) imports a key file into the KAS registry entry.
    - V(base_set) sets the base key for the KAS registry entry.
    required: yes
    choices: [import, base_set]
    type: str
  key_file:
    description:
    - Path to the key file on the Ansible controller.
    - Required when O(action=import).
    type: str
  key_type:
    description:
    - The key type, such as V(rsa) or V(ec).
    type: str
  algorithm:
    description:
    - The algorithm identifier, such as V(rsa-2048).
    type: str
  key_id:
    description:
    - The key ID to set as the base key.
    - Required when O(action=base_set).
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- A KAS registry entry must exist before importing keys. Use M(virtru.dsp_tructl.kas_registry) first.
- Key import operations are not naturally idempotent. Running the same import twice may result in duplicate keys.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: virtru.dsp_tructl.kas_registry
- module: virtru.dsp_tructl.kas_grant
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
- Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Import an RSA key into a KAS registry entry
  virtru.dsp_tructl.kas_key:
    kas_id: "550e8400-e29b-41d4-a716-446655440000"
    action: import
    key_file: /path/to/public-key.pem
    key_type: rsa
    algorithm: rsa-2048

- name: Set the base key for a KAS registry entry
  virtru.dsp_tructl.kas_key:
    kas_id: "550e8400-e29b-41d4-a716-446655440000"
    action: base_set
    key_id: "key-789-abc-012"
"""

RETURN = r"""
key:
    description: Key operation result details.
    returned: always
    type: dict
    sample: {"id": "key-789-abc-012", "kas_id": "550e8400-e29b-41d4-a716-446655440000", "key_type": "rsa"}
msg:
    description: Result message describing the operation performed.
    returned: always
    type: str
    sample: "Key imported successfully"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        kas_id=dict(type='str', required=True),
        action=dict(type='str', required=True, choices=['import', 'base_set']),
        key_file=dict(type='str'),
        key_type=dict(type='str'),
        algorithm=dict(type='str'),
        key_id=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('action', 'import', ['key_file']),
            ('action', 'base_set', ['key_id']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    action = module.params['action']
    kas_id = module.params['kas_id']
    result = dict(changed=False, msg='', key={})

    if module.check_mode:
        result['changed'] = True
        result['msg'] = 'Would perform %s on KAS %s' % (action, kas_id)
        module.exit_json(**result)

    if action == 'import':
        args = ['policy', 'kas-registry', 'key', 'import', '--kas-id', kas_id]
        args.extend(['--key-file', module.params['key_file']])
        if module.params.get('key_type'):
            args.extend(['--key-type', module.params['key_type']])
        if module.params.get('algorithm'):
            args.extend(['--algorithm', module.params['algorithm']])
        args.append('--json')
        output = runner.run_command(args, parse_json=True)
        result['changed'] = True
        result['key'] = output if isinstance(output, dict) else {}
        result['msg'] = 'Key imported successfully'

    elif action == 'base_set':
        args = [
            'policy', 'kas-registry', 'key', 'base', 'set',
            '--kas-id', kas_id,
            '--key-id', module.params['key_id'],
            '--json',
        ]
        output = runner.run_command(args, parse_json=True)
        result['changed'] = True
        result['key'] = output if isinstance(output, dict) else {}
        result['msg'] = 'Base key set successfully'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
