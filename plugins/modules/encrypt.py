#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: encrypt
short_description: Encrypt files to TDF format using tructl
version_added: "1.0.0"
description:
- Encrypts a file into Trusted Data Format (TDF) using C(tructl encrypt).
- Optionally applies attribute FQNs to control access to the encrypted data.
- This module is idempotent by default and skips encryption if the destination file already exists.
  Use O(force=true) to overwrite existing files.
options:
  src:
    description:
    - Path to the source file to encrypt.
    - The file must exist on the Ansible controller.
    required: yes
    type: str
  dest:
    description:
    - Output path for the encrypted TDF file.
    required: yes
    type: str
  attributes:
    description:
    - List of attribute FQNs to apply to the TDF.
    - Each attribute is in the format C(https://namespace/attr/name/value/val).
    type: list
    elements: str
  force:
    description:
    - If set to V(true), overwrite the destination file even if it already exists.
    - If set to V(false), the module will skip encryption when the destination exists.
    type: bool
    default: false
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- Authentication must be performed with M(virtru.dsp_tructl.auth) before encrypting files.
- The TDF format is a standard ZIP archive containing an encrypted payload and manifest.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: virtru.dsp_tructl.decrypt
- module: virtru.dsp_tructl.inspect
- module: virtru.dsp_tructl.auth
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
- Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Encrypt a file with classification attributes
  virtru.dsp_tructl.encrypt:
    src: /data/report.pdf
    dest: /data/report.pdf.tdf
    attributes:
      - "https://example.com/attr/classification/value/secret"

- name: Encrypt a file without attributes
  virtru.dsp_tructl.encrypt:
    src: /data/notes.txt
    dest: /data/notes.txt.tdf

- name: Force re-encryption of an existing TDF
  virtru.dsp_tructl.encrypt:
    src: /data/report.pdf
    dest: /data/report.pdf.tdf
    force: true
    attributes:
      - "https://example.com/attr/classification/value/confidential"

- name: Encrypt multiple files in a loop
  virtru.dsp_tructl.encrypt:
    src: "{{ item }}"
    dest: "{{ item }}.tdf"
    attributes:
      - "https://example.com/attr/classification/value/internal"
  loop:
    - /data/report-q1.pdf
    - /data/report-q2.pdf
"""

RETURN = r"""
dest:
    description: Path to the encrypted TDF file.
    returned: success
    type: str
    sample: "/data/report.pdf.tdf"
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        src=dict(type='str', required=True),
        dest=dict(type='str', required=True),
        attributes=dict(type='list', elements='str'),
        force=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    src = module.params['src']
    dest = module.params['dest']
    force = module.params['force']
    result = dict(changed=False, dest=dest)

    if not os.path.isfile(src):
        module.fail_json(msg="Source file does not exist: %s" % src)

    if os.path.isfile(dest) and not force:
        module.exit_json(**result)

    if module.check_mode:
        result['changed'] = True
        module.exit_json(**result)

    runner = TructlRunner(module)

    args = ['encrypt', src, '-o', dest]
    if module.params.get('attributes'):
        for attr in module.params['attributes']:
            args.extend(['--attr', attr])

    runner.run_command(args)
    result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
