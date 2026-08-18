#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: subject_condition_set
short_description: Manage DSP policy subject condition sets
version_added: "1.0.0"
description:
- Creates, deletes, or lists subject condition sets in the DSP platform.
- Subject condition sets define conditions based on IdP token claims that determine subject entitlements.
- This module is B(not) idempotent on create because subject condition sets have no natural key.
  Each call with O(state=present) will create a new subject condition set.
options:
  subject_sets:
    description:
    - A list of subject set definitions, each containing condition groups with boolean operators and conditions.
    - Passed as a JSON array to the tructl CLI.
    - Required when O(state=present).
    type: list
    elements: dict
  id:
    description:
    - The subject condition set ID.
    - Required when O(state=absent) to identify the set to delete.
    type: str
  state:
    description:
    - V(present) always creates a new subject condition set (not idempotent).
    - V(absent) deletes the subject condition set identified by O(id).
    - V(list) returns all subject condition sets.
    choices: [present, absent, list]
    default: present
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- Subject condition sets have no natural key, so O(state=present) always reports C(changed=true).
- It is recommended to define subject sets in a variables file rather than inline in playbooks.
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
- name: Create a subject condition set
  virtru.dsp_tructl.subject_condition_set:
    subject_sets:
      - condition_groups:
          - boolean_operator: AND
            conditions:
              - subject_external_selector_value: ".realm_access.roles"
                operator: IN
                subject_external_values:
                  - admin
    state: present

- name: List all subject condition sets
  virtru.dsp_tructl.subject_condition_set:
    state: list
  register: scs_result

- name: Delete a subject condition set by ID
  virtru.dsp_tructl.subject_condition_set:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
subject_condition_set:
    description: The subject condition set details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "subject_sets": []}
subject_condition_sets:
    description: List of all subject condition sets.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "subject_sets": []}]
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        subject_sets=dict(type='list', elements='dict'),
        id=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['subject_sets']),
            ('state', 'absent', ['id']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    result = dict(changed=False)

    if state == 'list':
        existing = runner.list_resources(['policy', 'subject-condition-sets'])
        result['subject_condition_sets'] = existing
        module.exit_json(**result)

    if state == 'present':
        # Not idempotent - always creates a new subject condition set
        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        output = runner.run_command(
            ['policy', 'subject-condition-sets', 'create',
             '--subject-sets', json.dumps(module.params['subject_sets']), '--json'],
            parse_json=True,
        )
        result['changed'] = True
        result['subject_condition_set'] = output

    elif state == 'absent':
        set_id = module.params['id']
        existing = runner.list_resources(['policy', 'subject-condition-sets'])
        current = runner.find_by_field(existing, 'id', set_id)
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(
                ['policy', 'subject-condition-sets', 'delete', '--id', set_id, '--force']
            )
            result['changed'] = True
            result['subject_condition_set'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
