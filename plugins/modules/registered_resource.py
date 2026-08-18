#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: registered_resource
short_description: Manage DSP policy registered resources
version_added: "1.0.0"
description:
- Creates, deletes, or lists registered resources in the DSP platform.
- Registered resources represent data assets that are protected by DSP policy.
- This module is idempotent when O(state=present) and checks for existing resources by O(name).
options:
  name:
    description:
    - The registered resource name.
    - Required when O(state=present).
    type: str
  values:
    description:
    - List of values to assign to the registered resource.
    type: list
    elements: str
  id:
    description:
    - The registered resource ID.
    - Required when O(state=absent) to identify the resource to delete.
    type: str
  state:
    description:
    - V(present) creates the registered resource if one does not exist with the given O(name).
    - V(absent) deletes the registered resource identified by O(id).
    - V(list) returns all registered resources.
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
- module: virtru.dsp_tructl.resource_mapping
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
- Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Create a registered resource
  virtru.dsp_tructl.registered_resource:
    name: "customer-database"
    values:
      - confidential
      - pii
    state: present

- name: List all registered resources
  virtru.dsp_tructl.registered_resource:
    state: list
  register: rr_result

- name: Delete a registered resource by ID
  virtru.dsp_tructl.registered_resource:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
registered_resource:
    description: The registered resource details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "name": "customer-database"}
registered_resources:
    description: List of all registered resources.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "name": "customer-database"}]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
        values=dict(type='list', elements='str'),
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

    # List current registered resources
    existing = runner.list_resources(['policy', 'registered-resources'])

    if state == 'list':
        result['registered_resources'] = existing
        module.exit_json(**result)

    if state == 'present':
        name = module.params['name']
        current = runner.find_by_field(existing, 'name', name)

        if current:
            result['registered_resource'] = current
            module.exit_json(**result)

        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        args = ['policy', 'registered-resources', 'create', '--name', name]
        if module.params.get('values'):
            for val in module.params['values']:
                args.extend(['--value', val])
        args.append('--json')
        output = runner.run_command(args, parse_json=True)
        result['changed'] = True
        result['registered_resource'] = output

    elif state == 'absent':
        resource_id = module.params['id']
        current = runner.find_by_field(existing, 'id', resource_id)
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(
                ['policy', 'registered-resources', 'delete', '--id', resource_id, '--force']
            )
            result['changed'] = True
            result['registered_resource'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
