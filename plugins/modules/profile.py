#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: profile
short_description: Manage tructl CLI profiles.
version_added: "1.0.0"
description:
  - Creates, removes, or lists tructl profiles.
  - Profiles store DSP platform endpoint configuration for the tructl CLI.
options:
  name:
    description:
      - The name of the profile to manage.
    required: true
    type: str
  endpoint:
    description:
      - The DSP platform endpoint URL.
      - Required when I(state=present).
    type: str
  default:
    description:
      - Whether to set this profile as the default profile.
    type: bool
    default: false
  state:
    description:
      - C(present) creates the profile if it does not exist.
      - C(absent) removes the profile.
      - C(list) returns all profiles.
    choices: [present, absent, list]
    default: present
    type: str
  tructl_bin:
    description:
      - Path to the tructl binary.
    type: str
    default: tructl
notes:
  - This module requires the tructl CLI to be installed on the target host.
  - Check mode is supported.
seealso:
  - module: dsp.tructl.auth
  - module: dsp.tructl.encrypt
author:
  - Virtru DSP Team
"""

EXAMPLES = r"""
- name: Create and set default profile
  dsp.tructl.profile:
    name: dsp-lab
    endpoint: "https://platform.dsp.lab"
    default: true

- name: List all profiles
  dsp.tructl.profile:
    name: unused
    state: list
  register: profiles

- name: Remove a profile
  dsp.tructl.profile:
    name: old-profile
    state: absent
"""

RETURN = r"""
profile:
  description: The profile details.
  returned: when state is present
  type: dict
  sample: {"name": "dsp-lab", "endpoint": "https://platform.dsp.lab"}
profiles:
  description: List of all profiles.
  returned: when state is list
  type: list
  sample: ["dsp-lab", "dsp-prod"]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dsp.tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        endpoint=dict(type='str'),
        default=dict(type='bool', default=False),
        state=dict(type='str', default='present', choices=['present', 'absent', 'list']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['endpoint']),
        ],
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    name = module.params['name']
    result = dict(changed=False)

    # Get current profiles
    stdout = runner.run_command(['profile', 'list'], check_rc=False)
    existing_profiles = stdout.strip() if stdout else ''

    if state == 'list':
        result['profiles'] = existing_profiles
        module.exit_json(**result)

    profile_exists = name in existing_profiles if existing_profiles else False

    if state == 'present':
        if not profile_exists:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(['profile', 'create', name, module.params['endpoint']])
            result['changed'] = True

        if module.params['default']:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(['profile', 'set-default', name])
            result['changed'] = True

        result['profile'] = dict(name=name, endpoint=module.params['endpoint'])

    elif state == 'absent':
        if profile_exists:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            runner.run_command(['profile', 'delete', name])
            result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
