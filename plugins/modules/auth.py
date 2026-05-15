#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: auth
short_description: Authenticate to DSP platform via tructl
version_added: "1.0.0"
description:
- Performs authentication to the DSP platform using C(tructl auth login).
- This should be run before any other tructl operations that require authentication.
- Authentication tokens are ephemeral so this module always reports C(changed=true).
options:
  client_id:
    description:
    - The OIDC client ID to authenticate with.
    - For public clients such as C(cli-client), no secret is required.
    required: yes
    type: str
  client_secret:
    description:
    - The OIDC client secret for confidential clients.
    - Not required for public clients.
    - When specified, it is recommended to set C(no_log=true) on the task to prevent credential leaks.
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- Always set C(no_log=true) when using O(client_secret) to prevent credential exposure in logs.
- This module requires C(tructl) to be installed on the Ansible controller.
- A profile should be configured with M(dsp.tructl.profile) before authenticating.
seealso:
- module: dsp.tructl.profile
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Authenticate with a public client
  dsp.tructl.auth:
    client_id: cli-client

- name: Authenticate with a confidential client
  dsp.tructl.auth:
    client_id: my-service
    client_secret: "{{ vault_client_secret }}"
  no_log: true

- name: Authenticate using a custom tructl binary path
  dsp.tructl.auth:
    client_id: cli-client
    tructl_bin: /usr/local/bin/tructl
"""

RETURN = r"""
msg:
    description: Authentication result message.
    returned: always
    type: str
    sample: "Successfully authenticated with client_id: cli-client"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dsp.tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        client_id=dict(type='str', required=True),
        client_secret=dict(type='str', required=False, no_log=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = dict(changed=True, msg='')

    if module.check_mode:
        result['msg'] = 'Would authenticate with client_id: %s' % module.params['client_id']
        module.exit_json(**result)

    runner = TructlRunner(module)

    args = ['auth', 'login', '-i', module.params['client_id']]
    if module.params.get('client_secret'):
        args.extend(['--client-secret', module.params['client_secret']])

    stdout = runner.run_command(args)
    result['msg'] = 'Successfully authenticated with client_id: %s' % module.params['client_id']
    module.exit_json(**result)


if __name__ == '__main__':
    main()
