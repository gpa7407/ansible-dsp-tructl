#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: obligation
short_description: Manage DSP policy obligations
version_added: "1.0.0"
description:
- Creates, deletes, or lists policy obligations in the DSP platform.
- Obligations define additional requirements that must be met when accessing protected data.
- This module is idempotent when O(state=present) and checks for existing obligations by O(name).
options:
  name:
    description:
    - The obligation name.
    - Required when O(state=present).
    type: str
  namespace:
    description:
    - The namespace ID or FQN the obligation belongs to.
    - Required when O(state=present).
    - Optional filter when O(state=list).
    type: str
  values:
    description:
    - List of values to assign to the obligation.
    type: list
    elements: str
  id:
    description:
    - The obligation ID.
    - One of O(id) or O(fqn) is required when O(state=absent).
    type: str
  fqn:
    description:
    - The obligation fully qualified name.
    - One of O(id) or O(fqn) is required when O(state=absent).
    type: str
  state:
    description:
    - V(present) creates the obligation if one does not exist with the given O(name).
    - V(absent) deletes the obligation identified by O(id) or O(fqn).
    - V(list) returns all obligations, optionally filtered by O(namespace).
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
- module: virtru.dsp_tructl.attribute
- module: virtru.dsp_tructl.namespace
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
- Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Create an obligation
  virtru.dsp_tructl.obligation:
    name: watermark
    namespace: "https://example.com/attr"
    values:
      - enabled
    state: present

- name: List all obligations
  virtru.dsp_tructl.obligation:
    state: list
  register: obl_result

- name: Delete an obligation by ID
  virtru.dsp_tructl.obligation:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent

- name: Delete an obligation by FQN
  virtru.dsp_tructl.obligation:
    fqn: "https://example.com/attr/obligation/watermark"
    state: absent
"""

RETURN = r"""
obligation:
    description: The obligation details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "name": "watermark"}
obligations:
    description: List of all obligations.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "name": "watermark"}]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
        namespace=dict(type='str'),
        values=dict(type='list', elements='str'),
        id=dict(type='str'),
        fqn=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['name', 'namespace']),
        ],
        required_one_of=[
            ['id', 'fqn', 'name'],
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    result = dict(changed=False)

    # Build list command with optional namespace filter
    list_args = ['policy', 'obligations']
    if module.params.get('namespace'):
        existing = runner.list_resources(list_args + ['--namespace', module.params['namespace']])
    else:
        existing = runner.list_resources(list_args)

    if state == 'list':
        result['obligations'] = existing
        module.exit_json(**result)

    if state == 'present':
        name = module.params['name']
        current = runner.find_by_field(existing, 'name', name)

        if current:
            result['obligation'] = current
            module.exit_json(**result)

        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        # DSP 2.0.7 requires the namespace reference as a UUID.
        namespace_id = runner.resolve_namespace_id(module.params['namespace'])
        args = ['policy', 'obligations', 'create',
                '--name', name, '--namespace', namespace_id]
        if module.params.get('values'):
            for val in module.params['values']:
                args.extend(['--value', val])
        args.append('--json')
        output = runner.run_command(args, parse_json=True)
        result['changed'] = True
        result['obligation'] = output

    elif state == 'absent':
        obl_id = module.params.get('id')
        obl_fqn = module.params.get('fqn')

        if not obl_id and not obl_fqn:
            module.fail_json(msg="One of 'id' or 'fqn' is required when state=absent")

        # Find current entry for idempotency check
        current = None
        if obl_id:
            current = runner.find_by_field(existing, 'id', obl_id)
        elif obl_fqn:
            current = runner.find_by_field(existing, 'fqn', obl_fqn)

        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            if obl_id:
                runner.run_command(['policy', 'obligations', 'delete', '--id', obl_id, '--force'])
            else:
                runner.run_command(['policy', 'obligations', 'delete', '--fqn', obl_fqn, '--force'])
            result['changed'] = True
            result['obligation'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
