#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: resource_mapping
short_description: Manage DSP policy resource mappings
version_added: "1.0.0"
description:
- Creates, deletes, or lists resource mappings in the DSP platform.
- Resource mappings link data tags and terms to platform attribute values, enabling automatic
  classification of data based on metadata extracted by the Data Tagging Service.
- This module is idempotent when O(state=present) and checks for existing mappings by O(attribute_value_id).
options:
  attribute_value_id:
    description:
    - The attribute value ID to map to.
    - Required when O(state=present).
    type: str
  terms:
    description:
    - List of resource mapping terms that will be matched against data tags.
    - Required when O(state=present).
    type: list
    elements: str
  id:
    description:
    - The resource mapping ID.
    - Required when O(state=absent) to identify the mapping to delete.
    type: str
  state:
    description:
    - V(present) creates the resource mapping if one does not exist for the given O(attribute_value_id).
    - V(absent) deletes the resource mapping identified by O(id).
    - V(list) returns all resource mappings.
    choices: [present, absent, list]
    default: present
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- Resource mappings connect the output of the Data Tagging Service to ABAC policy attributes.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: virtru.dsp_tructl.attribute
- module: virtru.dsp_tructl.subject_mapping
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Create a resource mapping for classification
  virtru.dsp_tructl.resource_mapping:
    attribute_value_id: "abc-123-def-456"
    terms:
      - "classification:secret"
    state: present

- name: Create a resource mapping with multiple terms
  virtru.dsp_tructl.resource_mapping:
    attribute_value_id: "abc-123-def-456"
    terms:
      - "classification:secret"
      - "sensitivity:high"
    state: present

- name: List all resource mappings
  virtru.dsp_tructl.resource_mapping:
    state: list
  register: rm_result

- name: Delete a resource mapping by ID
  virtru.dsp_tructl.resource_mapping:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
resource_mapping:
    description: The resource mapping details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "attribute_value_id": "abc-123-def-456", "terms": ["classification:secret"]}
resource_mappings:
    description: List of all resource mappings.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "attribute_value_id": "abc-123-def-456"}]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        attribute_value_id=dict(type='str'),
        terms=dict(type='list', elements='str'),
        id=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['attribute_value_id', 'terms']),
            ('state', 'absent', ['id']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    result = dict(changed=False)

    # List current resource mappings
    existing = runner.list_resources(['policy', 'resource-mappings'])

    if state == 'list':
        result['resource_mappings'] = existing
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
            result['resource_mapping'] = current
            module.exit_json(**result)

        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        args = ['policy', 'resource-mappings', 'create', '--attribute-value-id', attr_val_id]
        args.extend(['--terms', ','.join(module.params['terms'])])
        args.append('--json')
        output = runner.run_command(args, parse_json=True)
        result['changed'] = True
        result['resource_mapping'] = output

    elif state == 'absent':
        mapping_id = module.params['id']
        current = runner.find_by_field(existing, 'id', mapping_id)
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(['policy', 'resource-mappings', 'delete', '--id', mapping_id, '--force'])
            result['changed'] = True
            result['resource_mapping'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
