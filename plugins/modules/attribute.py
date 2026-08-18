#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: attribute
short_description: Manage DSP policy attributes.
version_added: "1.0.0"
description:
  - Creates, deactivates, or lists policy attributes in the DSP platform.
  - Attributes belong to namespaces and define access control dimensions.
  - Use this module to automate attribute lifecycle management as part of DSP policy configuration.
options:
  namespace:
    description:
      - The namespace name or ID the attribute belongs to.
    required: true
    type: str
  name:
    description:
      - The attribute name (e.g., C(classification)).
    required: true
    type: str
  rule:
    description:
      - The attribute rule type that governs how attribute values are evaluated during access decisions.
    choices: [ANY_OF, ALL_OF, HIERARCHY]
    type: str
  values:
    description:
      - List of attribute values to assign to the attribute.
    type: list
    elements: str
  state:
    description:
      - C(present) creates the attribute if it does not exist.
      - C(absent) deactivates the attribute.
      - C(list) returns all attributes.
    choices: [present, absent, list]
    default: present
    type: str
  tructl_bin:
    description:
      - Path to the tructl binary.
    type: str
    default: tructl
notes:
  - This module requires the C(tructl) CLI to be installed and accessible on the target host.
  - Check mode is supported for all states.
  - When I(state=absent), the attribute is deactivated rather than permanently deleted.
seealso:
  - module: virtru.dsp_tructl.namespace
  - module: virtru.dsp_tructl.subject_mapping
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
  - Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Create a classification attribute with hierarchy rule
  virtru.dsp_tructl.attribute:
    namespace: "https://example.com/attr"
    name: classification
    rule: HIERARCHY
    values:
      - public
      - internal
      - confidential
      - secret
    state: present

- name: Create a department attribute with anyOf rule
  virtru.dsp_tructl.attribute:
    namespace: "https://example.com/attr"
    name: department
    rule: ANY_OF
    values:
      - engineering
      - finance
      - hr
    state: present

- name: Deactivate an attribute
  virtru.dsp_tructl.attribute:
    namespace: "https://example.com/attr"
    name: classification
    state: absent

- name: List all attributes
  virtru.dsp_tructl.attribute:
    namespace: unused
    name: unused
    state: list
  register: attr_result
"""

RETURN = r"""
attribute:
  description: The attribute details returned from the DSP platform.
  returned: when state is present or absent
  type: dict
  sample:
    id: "b4e3c2a1-5678-4def-9abc-1234567890ab"
    name: "classification"
    rule: "HIERARCHY"
    namespace:
      id: "a1b2c3d4-5678-4def-9abc-abcdef123456"
      name: "https://example.com/attr"
    values:
      - value: "public"
      - value: "internal"
      - value: "confidential"
      - value: "secret"
    active: true
attributes:
  description: List of all attributes retrieved from the DSP platform.
  returned: when state is list
  type: list
  sample:
    - id: "b4e3c2a1-5678-4def-9abc-1234567890ab"
      name: "classification"
      rule: "HIERARCHY"
      namespace:
        id: "a1b2c3d4-5678-4def-9abc-abcdef123456"
        name: "https://example.com/attr"
      values:
        - value: "public"
        - value: "confidential"
      active: true
    - id: "c5f6d7e8-9012-4abc-def0-abcdef654321"
      name: "department"
      rule: "ANY_OF"
      namespace:
        id: "a1b2c3d4-5678-4def-9abc-abcdef123456"
        name: "https://example.com/attr"
      values:
        - value: "engineering"
        - value: "finance"
      active: true
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        namespace=dict(type='str', required=True),
        name=dict(type='str', required=True),
        rule=dict(type='str', choices=['ANY_OF', 'ALL_OF', 'HIERARCHY']),
        values=dict(type='list', elements='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['rule', 'values']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    namespace = module.params['namespace']
    name = module.params['name']
    result = dict(changed=False)

    # List current attributes
    existing = runner.list_resources(['policy', 'attributes'])

    if state == 'list':
        result['attributes'] = existing
        module.exit_json(**result)

    # Find attribute matching namespace (by name or ID) and attribute name
    current = None
    for attr in existing:
        attr_name = attr.get('name', '')
        attr_ns = attr.get('namespace', {})
        if isinstance(attr_ns, dict):
            ns_match = namespace in (attr_ns.get('name', ''), attr_ns.get('id', ''), attr_ns.get('fqn', ''))
        else:
            ns_match = attr_ns == namespace
        if attr_name == name and ns_match:
            current = attr
            break

    if state == 'present':
        if current:
            result['attribute'] = current
        else:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            # DSP 2.0.7's tructl requires the namespace as a UUID; resolve a
            # name/FQN to its ID (a UUID is returned unchanged).
            namespace_id = runner.resolve_namespace_id(namespace)
            args = [
                'policy', 'attributes', 'create',
                '--namespace', namespace_id,
                '--name', name,
                '--rule', module.params['rule'],
            ]
            for val in module.params['values']:
                args.extend(['--value', val])
            args.append('--json')
            output = runner.run_command(args, parse_json=True)
            result['changed'] = True
            result['attribute'] = output

    elif state == 'absent':
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(
                ['policy', 'attributes', 'deactivate', '--id', current['id'], '--force']
            )
            result['changed'] = True
            result['attribute'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
