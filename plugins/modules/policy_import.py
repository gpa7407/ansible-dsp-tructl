#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: policy_import
short_description: Import a policy bundle using tructl
version_added: "1.1.0"
description:
- Imports a policy bundle into the platform using C(tructl import).
- The bundle is typically produced by M(dsp.tructl.policy_export).
- This module always reports C(changed=true) because the import operation is not idempotent.
options:
  artifact:
    description:
    - Path to the policy bundle file to import.
    - The file must exist on the Ansible controller.
    required: yes
    type: str
  no_verify_signature:
    description:
    - If set to V(true), skip signature verification of the bundle during import.
    type: bool
    default: false
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
  host:
    description:
    - Platform endpoint URL.
    type: str
  tls_no_verify:
    description:
    - If set to V(true), skip TLS certificate verification.
    type: bool
    default: false
  client_creds:
    description:
    - Dictionary with C(clientId) and C(clientSecret) for authentication.
    type: dict
notes:
- This module always reports C(changed=true) because policy import is not idempotent.
- Authentication must be configured via O(client_creds) or a prior M(dsp.tructl.auth) call.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: dsp.tructl.policy_export
- module: dsp.tructl.provision
- module: dsp.tructl.auth
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Import a policy bundle
  dsp.tructl.policy_import:
    artifact: /tmp/demo-policy.bundle
    host: https://platform.dsp.vm
    client_creds:
      clientId: opentdf
      clientSecret: secret

- name: Import a policy bundle without signature verification
  dsp.tructl.policy_import:
    artifact: /tmp/demo-policy.bundle
    no_verify_signature: true
    host: https://platform.dsp.vm
    client_creds:
      clientId: opentdf
      clientSecret: secret
"""

RETURN = r"""
artifact:
    description: Path to the imported policy bundle.
    returned: success
    type: str
    sample: "/tmp/demo-policy.bundle"
stdout:
    description: Standard output from the tructl import command.
    returned: success
    type: str
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dsp.tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        artifact=dict(type='str', required=True),
        no_verify_signature=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    artifact = module.params['artifact']
    result = dict(changed=False, artifact=artifact)

    if not os.path.isfile(artifact):
        module.fail_json(msg="Artifact file does not exist: %s" % artifact)

    if module.check_mode:
        result['changed'] = True
        module.exit_json(**result)

    runner = TructlRunner(module)

    args = ['import', '--artifact', artifact]
    if module.params['no_verify_signature']:
        args.append('--no-verify-signature')

    stdout = runner.run_command(args)
    result['changed'] = True
    result['stdout'] = stdout

    module.exit_json(**result)


if __name__ == '__main__':
    main()
