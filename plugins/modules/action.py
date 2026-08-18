#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: action
short_description: Manage DSP policy actions
version_added: "1.0.0"
description:
- Creates, deletes, or lists policy actions in the DSP platform.
- Actions define the operations (e.g., DECRYPT, TRANSMIT) that can be granted via subject mappings.
- This module is idempotent when O(state=present) and checks for existing actions by O(name).
options:
  name:
    description:
    - The action name (e.g., C(DECRYPT), C(TRANSMIT)).
    - Required when O(state=present).
    type: str
  id:
    description:
    - The action ID.
    - Required when O(state=absent) to identify the action to delete.
    type: str
  state:
    description:
    - V(present) creates the action if one does not exist with the given O(name).
    - V(absent) deletes the action identified by O(id).
    - V(list) returns all actions.
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
- module: virtru.dsp_tructl.subject_mapping
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
- Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Create a DECRYPT action
  virtru.dsp_tructl.action:
    name: DECRYPT
    state: present

- name: List all actions
  virtru.dsp_tructl.action:
    state: list
  register: action_result

- name: Delete an action by ID
  virtru.dsp_tructl.action:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
action:
    description: The action details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "name": "DECRYPT"}
actions:
    description: List of all actions.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "name": "DECRYPT"}]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
        id=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['name']),
            ('state', 'absent', ['id']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    result = dict(changed=False)

    # List current actions
    existing = runner.list_resources(['policy', 'actions'])

    if state == 'list':
        result['actions'] = existing
        module.exit_json(**result)

    if state == 'present':
        name = module.params['name']
        current = runner.find_by_field(existing, 'name', name)

        if current:
            result['action'] = current
            module.exit_json(**result)

        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        output = runner.run_command(
            ['policy', 'actions', 'create', '--name', name, '--json'],
            parse_json=True,
        )
        result['changed'] = True
        result['action'] = output

    elif state == 'absent':
        action_id = module.params['id']
        current = runner.find_by_field(existing, 'id', action_id)
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(['policy', 'actions', 'delete', '--id', action_id, '--force'])
            result['changed'] = True
            result['action'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
