#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: decrypt
short_description: Decrypt TDF files using tructl
version_added: "1.0.0"
description:
- Decrypts a Trusted Data Format (TDF) file back to its original format using C(tructl decrypt).
- The KAS performs an authorization check before releasing the decryption key.
- This module is idempotent by default and skips decryption if the destination file already exists.
  Use O(force=true) to overwrite existing files.
options:
  src:
    description:
    - Path to the TDF file to decrypt.
    - The file must exist on the Ansible controller.
    required: yes
    type: str
  dest:
    description:
    - Output path for the decrypted file.
    - If not specified, C(tructl) uses its default output naming convention.
    type: str
  force:
    description:
    - If set to V(true), overwrite the destination file even if it already exists.
    - If set to V(false), the module will skip decryption when the destination exists.
    type: bool
    default: false
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- Authentication must be performed with M(virtru.dsp_tructl.auth) before decrypting files.
- The authenticated user must have the required attributes to satisfy the TDF's access policy.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: virtru.dsp_tructl.encrypt
- module: virtru.dsp_tructl.inspect
- module: virtru.dsp_tructl.auth
author:
- Virtru DSP Team
"""

EXAMPLES = r"""
- name: Decrypt a TDF file to a specific path
  virtru.dsp_tructl.decrypt:
    src: /data/report.pdf.tdf
    dest: /data/report.pdf

- name: Decrypt with default output name
  virtru.dsp_tructl.decrypt:
    src: /data/notes.txt.tdf

- name: Force re-decryption of an existing file
  virtru.dsp_tructl.decrypt:
    src: /data/report.pdf.tdf
    dest: /data/report.pdf
    force: true
"""

RETURN = r"""
dest:
    description: Path to the decrypted file.
    returned: success
    type: str
    sample: "/data/report.pdf"
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        src=dict(type='str', required=True),
        dest=dict(type='str'),
        force=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    src = module.params['src']
    dest = module.params.get('dest')
    force = module.params['force']
    result = dict(changed=False, dest=dest or '')

    if not os.path.isfile(src):
        module.fail_json(msg="Source TDF file does not exist: %s" % src)

    if dest and os.path.isfile(dest) and not force:
        module.exit_json(**result)

    if module.check_mode:
        result['changed'] = True
        module.exit_json(**result)

    runner = TructlRunner(module)

    args = ['decrypt', src]
    if dest:
        args.extend(['-o', dest])

    runner.run_command(args)
    result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
