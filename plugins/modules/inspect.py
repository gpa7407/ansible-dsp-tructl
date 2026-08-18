#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Virtru
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: inspect
short_description: Inspect TDF file metadata
version_added: "1.0.0"
description:
- Inspects a Trusted Data Format (TDF) file and returns its metadata.
- Returns information including the policy, attributes, key access objects, and assertions.
- This is a read-only operation that never changes state and always reports C(changed=false).
options:
  src:
    description:
    - Path to the TDF file to inspect.
    - The file must exist on the Ansible controller.
    required: yes
    type: str
  tructl_bin:
    description:
    - Path to the C(tructl) binary.
    type: str
    default: tructl
notes:
- This module does not require authentication as it only reads the TDF manifest locally.
- The module first attempts JSON output, falling back to raw text output if JSON is not supported.
- This module requires C(tructl) to be installed on the Ansible controller.
seealso:
- module: virtru.dsp_tructl.encrypt
- module: virtru.dsp_tructl.decrypt
extends_documentation_fragment:
- virtru.dsp_tructl.tructl
author:
- Virtru (@virtru)
"""

EXAMPLES = r"""
- name: Inspect a TDF file
  virtru.dsp_tructl.inspect:
    src: /data/report.pdf.tdf
  register: tdf_info

- name: Display TDF metadata
  ansible.builtin.debug:
    var: tdf_info.tdf_info

- name: Check TDF attributes before processing
  virtru.dsp_tructl.inspect:
    src: /data/sensitive.tdf
  register: tdf_meta

- name: Show raw output if JSON is not available
  ansible.builtin.debug:
    var: tdf_meta.raw_output
  when: tdf_meta.raw_output | length > 0
"""

RETURN = r"""
tdf_info:
    description: Parsed TDF metadata including policy, attributes, and key access objects.
    returned: success
    type: dict
    sample: {"policy": {"body": {"dataAttributes": []}}, "schemaVersion": "1.0"}
raw_output:
    description: Raw C(tructl inspect) output when JSON parsing is not available.
    returned: when JSON output is not supported
    type: str
    sample: "TDF Manifest:\n  Schema: 1.0\n  Attributes: ..."
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.virtru.dsp_tructl.plugins.module_utils.tructl_common import TructlRunner, common_argument_spec


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        src=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    src = module.params['src']
    result = dict(changed=False, tdf_info={}, raw_output='')

    if not os.path.isfile(src):
        module.fail_json(msg="TDF file does not exist: %s" % src)

    runner = TructlRunner(module)

    # Try JSON output first, fall back to raw
    output = runner.run_command(['inspect', src, '--json'], check_rc=False, parse_json=True)
    if isinstance(output, (dict, list)):
        result['tdf_info'] = output
    else:
        raw = runner.run_command(['inspect', src])
        result['raw_output'] = raw

    module.exit_json(**result)


if __name__ == '__main__':
    main()
