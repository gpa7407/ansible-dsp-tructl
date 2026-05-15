#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: kas_registry
short_description: Manage DSP Key Access Server registry entries
version_added: "1.0.0"
description:
- Creates, removes, or lists Key Access Server (KAS) registry entries in the DSP platform.
- KAS servers manage encryption key exchanges and enforce policy through key grant or withhold decisions.
- This module is idempotent when O(state=present) and checks for existing entries by O(name) or O(uri).
options:
  name:
    description:
    - The KAS server name.
    - Required when O(state=present).
    type: str
  uri:
    description:
    - The KAS server URI endpoint.
    - Required when O(state=present).
    type: str
  id:
    description:
    - The KAS registry entry ID.
    - Required when O(state=absent) to identify the entry to delete.
    type: str
  state:
    description:
    - V(present) creates the KAS registry entry if one does not exist with the given O(name) or O(uri).
    - V(absent) deletes the KAS registry entry identified by O(id).
    - V(list) returns all KAS registry entries.
    choices: [present, absent, list]
    default: present
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- The KAS is the Policy Enforcement Point (PEP) in the NIST ABAC model.
- After registering a KAS, use M(dsp.tructl.kas_key) to import keys.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: dsp.tructl.kas_key
- module: dsp.tructl.kas_grant
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Register a KAS server
  dsp.tructl.kas_registry:
    name: primary-kas
    uri: "https://platform.dsp.lab/kas"
    state: present

- name: List all KAS registry entries
  dsp.tructl.kas_registry:
    state: list
  register: kas_result

- name: Remove a KAS registry entry by ID
  dsp.tructl.kas_registry:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
kas_registry:
    description: The KAS registry entry details.
    returned: when state is present or absent
    type: dict
    sample: {"id": "550e8400-e29b-41d4-a716-446655440000", "name": "primary-kas", "uri": "https://platform.dsp.lab/kas"}
kas_registries:
    description: List of all KAS registry entries.
    returned: when state is list
    type: list
    sample: [{"id": "550e8400-e29b-41d4-a716-446655440000", "name": "primary-kas", "uri": "https://platform.dsp.lab/kas"}]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dsp.tructl.plugins.module_utils.tructl_common import TructlRunner, state_argument_spec


def main():
    argument_spec = state_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
        uri=dict(type='str'),
        id=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['name', 'uri']),
            ('state', 'absent', ['id']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    result = dict(changed=False)

    # List current KAS registry entries
    existing = runner.list_resources(['policy', 'kas-registry'])

    if state == 'list':
        result['kas_registries'] = existing
        module.exit_json(**result)

    if state == 'present':
        name = module.params['name']
        uri = module.params['uri']

        # Check by name or URI
        current = runner.find_by_field(existing, 'name', name)
        if not current:
            current = runner.find_by_field(existing, 'uri', uri)

        if current:
            result['kas_registry'] = current
            module.exit_json(**result)

        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        output = runner.run_command(
            ['policy', 'kas-registry', 'create', '--uri', uri, '--name', name, '--json'],
            parse_json=True,
        )
        result['changed'] = True
        result['kas_registry'] = output

    elif state == 'absent':
        entry_id = module.params['id']
        current = runner.find_by_field(existing, 'id', entry_id)
        if current:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(['policy', 'kas-registry', 'delete', '--id', entry_id, '--force'])
            result['changed'] = True
            result['kas_registry'] = current

    module.exit_json(**result)


if __name__ == '__main__':
    main()
