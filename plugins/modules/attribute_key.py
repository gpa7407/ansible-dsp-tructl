#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: attribute_key
short_description: Assign or remove KAS keys on policy attributes
version_added: "1.0.0"
description:
- Assigns or removes a KAS key on a policy attribute definition.
- Uses C(tructl policy attributes key assign) and C(tructl policy attributes key remove).
- Always reports C(changed=true) because the assign operation is safe to repeat and no idempotency check is performed.
options:
  attribute:
    description:
    - The attribute URI or ID to manage keys for.
    required: yes
    type: str
  key_id:
    description:
    - The KAS key ID to assign or remove.
    required: yes
    type: str
  state:
    description:
    - V(present) assigns the key to the attribute.
    - V(absent) removes the key from the attribute.
    choices: [present, absent]
    default: present
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- The attribute must already exist. Use M(virtru.dsp_tructl.attribute) to create it first.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: virtru.dsp_tructl.attribute
- module: virtru.dsp_tructl.kas_key
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
- Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Assign a KAS key to an attribute
  virtru.dsp_tructl.attribute_key:
    attribute: "https://example.com/attr/classification"
    key_id: "key-789-abc-012"
    state: present

- name: Remove a KAS key from an attribute
  virtru.dsp_tructl.attribute_key:
    attribute: "https://example.com/attr/classification"
    key_id: "key-789-abc-012"
    state: absent
"""

RETURN = r"""
result:
    description: Command output from the key operation.
    returned: on assign
    type: dict
    sample: {"attribute": "https://example.com/attr/classification", "key_id": "key-789-abc-012"}
msg:
    description: Result message describing the operation performed.
    returned: always
    type: str
    sample: "Key assigned to attribute successfully"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        attribute=dict(type='str', required=True),
        key_id=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    attribute = module.params['attribute']
    key_id = module.params['key_id']
    result = dict(changed=False, msg='', result={})

    if module.check_mode:
        result['changed'] = True
        result['msg'] = 'Would %s key %s on attribute %s' % (
            'assign' if state == 'present' else 'remove', key_id, attribute)
        module.exit_json(**result)

    if state == 'present':
        args = [
            'policy', 'attributes', 'key', 'assign',
            '--attribute', attribute,
            '--key-id', key_id,
            '--json',
        ]
        output = runner.run_command(args, parse_json=True)
        result['changed'] = True
        result['result'] = output if isinstance(output, dict) else {}
        result['msg'] = 'Key assigned to attribute successfully'

    elif state == 'absent':
        args = [
            'policy', 'attributes', 'key', 'remove',
            '--attribute', attribute,
            '--key-id', key_id,
        ]
        runner.run_command(args)
        result['changed'] = True
        result['msg'] = 'Key removed from attribute successfully'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
