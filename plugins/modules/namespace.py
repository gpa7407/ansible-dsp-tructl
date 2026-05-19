#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: namespace
short_description: Manage DSP policy attribute namespaces.
version_added: "1.0.0"
description:
  - Creates, deactivates, or lists attribute namespaces in the DSP platform.
  - Uses the C(tructl) CLI to interact with the DSP policy service.
options:
  name:
    description:
      - The namespace name (e.g., C(https://example.com/attr)).
      - Required for all states, though ignored when I(state=list).
    required: yes
    type: str
  state:
    description:
      - C(present) creates the namespace if it does not exist.
      - C(absent) deactivates the namespace.
      - C(list) returns all namespaces.
    choices: [present, absent, list]
    default: present
    type: str
  tructl_bin:
    description:
      - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
  - This module requires the C(tructl) CLI to be installed and configured on the target host.
  - Check mode is supported for C(present) and C(absent) states.
seealso:
  - module: virtru.dsp_tructl.attribute
author:
  - Virtru DSP Team
"""

EXAMPLES = r"""
- name: Create a namespace
  virtru.dsp_tructl.namespace:
    name: "https://example.com/attr"
    state: present

- name: List all namespaces
  virtru.dsp_tructl.namespace:
    name: unused
    state: list
  register: ns_result

- name: Deactivate a namespace
  virtru.dsp_tructl.namespace:
    name: "https://example.com/attr"
    state: absent
"""

RETURN = r"""
namespace:
  description: The namespace details returned from the DSP platform.
  returned: when state is present or absent
  type: dict
  sample:
    id: "e2e4d5f6-7890-1234-abcd-ef0123456789"
    name: "https://example.com/attr"
    active: true
    fqn: "https://example.com/attr"
namespaces:
  description: List of all namespaces registered in the DSP platform.
  returned: when state is list
  type: list
  sample:
    - id: "e2e4d5f6-7890-1234-abcd-ef0123456789"
      name: "https://example.com/attr"
      active: true
      fqn: "https://example.com/attr"
    - id: "a1b2c3d4-5678-9012-abcd-ef3456789012"
      name: "https://acme.org/attr"
      active: true
      fqn: "https://acme.org/attr"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    name = module.params['name']
    result = dict(changed=False)

    # List current namespaces
    existing = runner.list_resources(['policy', 'attributes', 'namespaces'])

    if state == 'list':
        result['namespaces'] = existing
        module.exit_json(**result)

    current = runner.find_by_field(existing, 'name', name)

    if state == 'present':
        if current:
            result['namespace'] = current
        else:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            output = runner.run_command(
                ['policy', 'attributes', 'namespaces', 'create', '--name', name, '--json'],
                parse_json=True,
            )
            result['changed'] = True
            result['namespace'] = output

    elif state == 'absent':
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(
                ['policy', 'attributes', 'namespaces', 'deactivate', '--id', current['id'], '--force']
            )
            result['changed'] = True
            result['namespace'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
