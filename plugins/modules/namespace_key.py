#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: namespace_key
short_description: Assign or remove KAS keys on policy namespaces
version_added: "1.0.0"
description:
- Assigns or removes a KAS key on a policy attribute namespace.
- Uses C(tructl policy attributes namespaces key assign) and C(tructl policy attributes namespaces key remove).
- Always reports C(changed=true) because the assign operation is safe to repeat and no idempotency check is performed.
options:
  namespace:
    description:
    - The namespace URI or ID to manage keys for.
    required: yes
    type: str
  key_id:
    description:
    - The KAS key ID to assign or remove.
    required: yes
    type: str
  state:
    description:
    - V(present) assigns the key to the namespace.
    - V(absent) removes the key from the namespace.
    choices: [present, absent]
    default: present
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- The namespace must already exist. Use M(virtru.dsp_tructl.namespace) to create it first.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: virtru.dsp_tructl.namespace
- module: virtru.dsp_tructl.kas_key
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
- Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Assign a KAS key to a namespace
  virtru.dsp_tructl.namespace_key:
    namespace: "https://example.com/attr/classification"
    key_id: "key-789-abc-012"
    state: present

- name: Remove a KAS key from a namespace
  virtru.dsp_tructl.namespace_key:
    namespace: "https://example.com/attr/classification"
    key_id: "key-789-abc-012"
    state: absent
"""

RETURN = r"""
result:
    description: Command output from the key operation.
    returned: on assign
    type: dict
    sample: {"namespace": "https://example.com/attr/classification", "key_id": "key-789-abc-012"}
msg:
    description: Result message describing the operation performed.
    returned: always
    type: str
    sample: "Key assigned to namespace successfully"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        namespace=dict(type='str', required=True),
        key_id=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    runner = TructlRunner(module)
    state = module.params['state']
    namespace = module.params['namespace']
    key_id = module.params['key_id']
    result = dict(changed=False, msg='', result={})

    if module.check_mode:
        result['changed'] = True
        result['msg'] = 'Would %s key %s on namespace %s' % (
            'assign' if state == 'present' else 'remove', key_id, namespace)
        module.exit_json(**result)

    # DSP 2.0.7 requires the namespace reference as a UUID.
    namespace_id = runner.resolve_namespace_id(namespace)

    if state == 'present':
        args = [
            'policy', 'attributes', 'namespaces', 'key', 'assign',
            '--namespace', namespace_id,
            '--key-id', key_id,
            '--json',
        ]
        output = runner.run_command(args, parse_json=True)
        result['changed'] = True
        result['result'] = output if isinstance(output, dict) else {}
        result['msg'] = 'Key assigned to namespace successfully'

    elif state == 'absent':
        args = [
            'policy', 'attributes', 'namespaces', 'key', 'remove',
            '--namespace', namespace_id,
            '--key-id', key_id,
        ]
        runner.run_command(args)
        result['changed'] = True
        result['msg'] = 'Key removed from namespace successfully'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
