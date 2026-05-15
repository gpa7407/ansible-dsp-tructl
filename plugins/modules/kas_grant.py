#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: kas_grant
short_description: Migrate KAS grants
version_added: "1.0.0"
description:
- Runs C(tructl migrate kas-grants) to migrate KAS grant configurations.
- This is typically a one-time operation performed during platform setup or upgrade.
- The module always reports C(changed=true) as it cannot determine if migration work was performed.
options:
  interactive:
    description:
    - Use interactive mode (C(-i) flag).
    type: bool
    default: true
  commit:
    description:
    - Commit the migration (C(-c) flag).
    - When set to V(false), performs a dry run without applying changes.
    type: bool
    default: true
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- This is typically run once after KAS registry and key configuration is complete.
- Use O(commit=false) to preview what the migration would do before committing.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: dsp.tructl.kas_registry
- module: dsp.tructl.kas_key
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Migrate KAS grants with commit
  dsp.tructl.kas_grant:
    interactive: true
    commit: true

- name: Preview KAS grants migration without committing
  dsp.tructl.kas_grant:
    interactive: true
    commit: false
  register: migration_preview
"""

RETURN = r"""
msg:
    description: Migration result message.
    returned: always
    type: str
    sample: "KAS grants migration completed"
stdout:
    description: Raw command output from the migration.
    returned: always
    type: str
    sample: "Migrated 3 grants successfully"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dsp.tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        interactive=dict(type='bool', default=True),
        commit=dict(type='bool', default=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = dict(changed=False, msg='', stdout='')

    if module.check_mode:
        result['msg'] = 'Would run kas-grants migration'
        result['changed'] = True
        module.exit_json(**result)

    runner = TructlRunner(module)

    args = ['migrate', 'kas-grants']
    if module.params['interactive']:
        args.append('-i')
    if module.params['commit']:
        args.append('-c')

    stdout = runner.run_command(args)
    result['changed'] = True
    result['stdout'] = stdout
    result['msg'] = 'KAS grants migration completed'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
