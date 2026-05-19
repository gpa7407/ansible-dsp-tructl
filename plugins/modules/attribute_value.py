#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: attribute_value
short_description: Manage DSP policy attribute values
version_added: "1.1.0"
description:
- Creates, deactivates, or lists attribute values in the DSP platform.
- Attribute values are the individual choices within a policy attribute (e.g., C(public), C(secret)).
- This module is idempotent when O(state=present) and checks for existing values by O(value) name
  within the specified O(attribute_id).
options:
  attribute_id:
    description:
    - The parent attribute ID that this value belongs to.
    - Required when O(state=present).
    - Optional filter when O(state=list).
    type: str
  value:
    description:
    - The attribute value name (e.g., C(public), C(confidential)).
    - Required when O(state=present).
    type: str
  id:
    description:
    - The attribute value ID.
    - Required when O(state=absent) to identify the value to deactivate.
    type: str
  state:
    description:
    - V(present) creates the attribute value if one does not exist with the given O(value) name.
    - V(absent) deactivates the attribute value identified by O(id).
    - V(list) returns all attribute values, optionally filtered by O(attribute_id).
    choices: [present, absent, list]
    default: present
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- When deactivating (O(state=absent)), the value is soft-deleted rather than permanently removed.
- This module requires C(tructl) to be installed on the Ansible controller.
- Check mode is supported for all states.
seealso:
- module: virtru.dsp_tructl.attribute
- module: virtru.dsp_tructl.namespace
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Create an attribute value
  virtru.dsp_tructl.attribute_value:
    attribute_id: "abc-123-def-456"
    value: confidential
    state: present

- name: List all attribute values
  virtru.dsp_tructl.attribute_value:
    state: list
  register: val_result

- name: List attribute values for a specific attribute
  virtru.dsp_tructl.attribute_value:
    attribute_id: "abc-123-def-456"
    state: list
  register: val_result

- name: Deactivate an attribute value by ID
  virtru.dsp_tructl.attribute_value:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
attribute_value:
    description: The attribute value details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "value": "confidential", "active": true}
attribute_values:
    description: List of all attribute values.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "value": "confidential", "active": true}]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        attribute_id=dict(type='str'),
        value=dict(type='str'),
        id=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['attribute_id', 'value']),
            ('state', 'absent', ['id']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    result = dict(changed=False)

    # For absent state, deactivate directly by ID without listing
    if state == 'absent':
        val_id = module.params['id']
        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)
        runner.run_command(['policy', 'attributes', 'values', 'deactivate', '--id', val_id])
        result['changed'] = True
        result['attribute_value'] = {'id': val_id}
        module.exit_json(**result)

    # Build list command (requires attribute_id for the CLI)
    list_args = ['policy', 'attributes', 'values']
    if module.params.get('attribute_id'):
        existing = runner.list_resources(list_args + ['--attribute-id', module.params['attribute_id']])
    else:
        existing = runner.list_resources(list_args)

    if state == 'list':
        result['attribute_values'] = existing
        module.exit_json(**result)

    if state == 'present':
        attribute_id = module.params['attribute_id']
        value = module.params['value']

        # Check if value already exists by the 'value' field
        current = runner.find_by_field(existing, 'value', value)

        if current:
            result['attribute_value'] = current
            module.exit_json(**result)

        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        output = runner.run_command(
            ['policy', 'attributes', 'values', 'create',
             '--attribute-id', attribute_id, '--value', value, '--json'],
            parse_json=True,
        )
        result['changed'] = True
        result['attribute_value'] = output

    elif state == 'absent':
        value_id = module.params['id']
        current = runner.find_by_field(existing, 'id', value_id)
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(
                ['policy', 'attributes', 'values', 'deactivate', '--id', value_id, '--force']
            )
            result['changed'] = True
            result['attribute_value'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
