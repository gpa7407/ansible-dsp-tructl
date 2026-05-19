#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: subject_mapping
short_description: Manage DSP policy subject mappings
version_added: "1.0.0"
description:
- Creates, deletes, or lists subject mappings in the DSP platform.
- Subject mappings link IdP identity attributes to policy attribute values, defining which subjects
  can perform which actions on data protected by specific attributes.
- This module is idempotent when O(state=present) and checks for existing mappings by O(attribute_value_id).
options:
  attribute_value_id:
    description:
    - The attribute value ID to map.
    - Required when O(state=present).
    type: str
  actions:
    description:
    - List of action objects for the mapping.
    - Each action is a dictionary with a C(standard) key specifying the action type.
    - Common actions include C(DECRYPT), C(TRANSMIT).
    - Required when O(state=present).
    type: list
    elements: dict
  subject_condition_sets:
    description:
    - Subject condition set definitions as a list of dictionaries.
    - Each set contains C(condition_groups) with boolean operators and conditions.
    - Conditions reference IdP token claims via C(subject_external_selector_value).
    - Required when O(state=present).
    type: list
    elements: dict
  id:
    description:
    - The subject mapping ID.
    - Required when O(state=absent) to identify the mapping to delete.
    type: str
  state:
    description:
    - V(present) creates the subject mapping if one does not exist for the given O(attribute_value_id).
    - V(absent) deletes the subject mapping identified by O(id).
    - V(list) returns all subject mappings.
    choices: [present, absent, list]
    default: present
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- Subject condition sets have a complex nested structure. It is recommended to define them
  in a variables file rather than inline in playbooks.
- The module passes O(actions) and O(subject_condition_sets) as JSON to the tructl CLI.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: virtru.dsp_tructl.attribute
- module: virtru.dsp_tructl.resource_mapping
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Create a subject mapping granting DECRYPT to admins
  virtru.dsp_tructl.subject_mapping:
    attribute_value_id: "abc-123-def-456"
    actions:
      - standard: DECRYPT
    subject_condition_sets:
      - condition_groups:
          - boolean_operator: AND
            conditions:
              - subject_external_selector_value: ".realm_access.roles"
                operator: IN
                subject_external_values:
                  - admin
    state: present

- name: List all subject mappings
  virtru.dsp_tructl.subject_mapping:
    state: list
  register: sm_result

- name: Delete a subject mapping by ID
  virtru.dsp_tructl.subject_mapping:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
subject_mapping:
    description: The subject mapping details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "attribute_value_id": "abc-123-def-456", "actions": [{"standard": "DECRYPT"}]}
subject_mappings:
    description: List of all subject mappings.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "attribute_value_id": "abc-123-def-456"}]
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        attribute_value_id=dict(type='str'),
        actions=dict(type='list', elements='dict'),
        subject_condition_sets=dict(type='list', elements='dict'),
        id=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['attribute_value_id', 'actions', 'subject_condition_sets']),
            ('state', 'absent', ['id']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    result = dict(changed=False)

    # List current subject mappings
    existing = runner.list_resources(['policy', 'subject-mappings'])

    if state == 'list':
        result['subject_mappings'] = existing
        module.exit_json(**result)

    if state == 'present':
        attr_val_id = module.params['attribute_value_id']

        # Check if mapping already exists for this attribute value
        # The list response nests attribute value as attribute_value.id
        current = None
        for item in (existing or []):
            av = item.get('attribute_value', {})
            if isinstance(av, dict) and av.get('id') == attr_val_id:
                current = item
                break
        if not current:
            current = runner.find_by_field(existing, 'attribute_value_id', attr_val_id)
        if current:
            result['subject_mapping'] = current
            module.exit_json(**result)

        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        # Build action flags: --action for each action standard name
        args = [
            'policy', 'subject-mappings', 'create',
            '--attribute-value-id', attr_val_id,
        ]
        for action in module.params['actions']:
            args.extend(['--action', action.get('standard', action.get('name', ''))])
        args.extend([
            '--subject-condition-set-new', json.dumps(module.params['subject_condition_sets']),
            '--json',
        ])
        output = runner.run_command(args, parse_json=True)
        result['changed'] = True
        result['subject_mapping'] = output

    elif state == 'absent':
        mapping_id = module.params['id']
        current = runner.find_by_field(existing, 'id', mapping_id)
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(['policy', 'subject-mappings', 'delete', '--id', mapping_id, '--force'])
            result['changed'] = True
            result['subject_mapping'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
