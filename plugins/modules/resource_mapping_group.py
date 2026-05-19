#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: resource_mapping_group
short_description: Manage DSP policy resource mapping groups
version_added: "1.1.0"
description:
- Creates, deletes, or lists resource mapping groups in the DSP platform.
- Resource mapping groups organize resource mappings under a namespace for logical grouping.
- This module is idempotent when O(state=present) and checks for existing groups by O(name).
options:
  namespace_id:
    description:
    - The namespace ID the resource mapping group belongs to.
    - Required when O(state=present).
    type: str
  name:
    description:
    - The resource mapping group name.
    - Required when O(state=present).
    type: str
  id:
    description:
    - The resource mapping group ID.
    - Required when O(state=absent) to identify the group to delete.
    type: str
  state:
    description:
    - V(present) creates the resource mapping group if one does not exist with the given O(name).
    - V(absent) deletes the resource mapping group identified by O(id).
    - V(list) returns all resource mapping groups.
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
- module: virtru.dsp_tructl.namespace
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Create a resource mapping group
  virtru.dsp_tructl.resource_mapping_group:
    namespace_id: "abc-123-def-456"
    name: classification-mappings
    state: present

- name: List all resource mapping groups
  virtru.dsp_tructl.resource_mapping_group:
    state: list
  register: rmg_result

- name: Delete a resource mapping group by ID
  virtru.dsp_tructl.resource_mapping_group:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
resource_mapping_group:
    description: The resource mapping group details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "namespace_id": "abc-123-def-456", "name": "classification-mappings"}
resource_mapping_groups:
    description: List of all resource mapping groups.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "namespace_id": "abc-123-def-456", "name": "classification-mappings"}]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        namespace_id=dict(type='str'),
        name=dict(type='str'),
        id=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['namespace_id', 'name']),
            ('state', 'absent', ['id']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    result = dict(changed=False)

    # List current resource mapping groups
    existing = runner.list_resources(['policy', 'resource-mapping-groups'])

    if state == 'list':
        result['resource_mapping_groups'] = existing
        module.exit_json(**result)

    if state == 'present':
        name = module.params['name']
        current = runner.find_by_field(existing, 'name', name)

        if current:
            result['resource_mapping_group'] = current
            module.exit_json(**result)

        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        output = runner.run_command(
            ['policy', 'resource-mapping-groups', 'create',
             '--namespace-id', module.params['namespace_id'], '--name', name, '--json'],
            parse_json=True,
        )
        result['changed'] = True
        result['resource_mapping_group'] = output

    elif state == 'absent':
        group_id = module.params['id']
        current = runner.find_by_field(existing, 'id', group_id)
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(
                ['policy', 'resource-mapping-groups', 'delete', '--id', group_id, '--force']
            )
            result['changed'] = True
            result['resource_mapping_group'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
