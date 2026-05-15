# inspect

Inspect TDF file metadata.

## Synopsis

- Inspects a Trusted Data Format (TDF) file and returns its metadata.
- Returns information including the policy, attributes, key access objects, and assertions.
- This is a read-only operation that never changes state and always reports `changed=false`.

## Parameters

| Parameter    | Type | Required | Default  | Description                                                                     |
| ------------ | ---- | -------- | -------- | ------------------------------------------------------------------------------- |
| `src`        | str  | yes      |          | Path to the TDF file to inspect. The file must exist on the Ansible controller. |
| `tructl_bin` | str  | no       | `tructl` | Path to the `tructl` binary.                                                    |

## Notes

- This module does not require authentication as it only reads the TDF manifest locally.
- The module first attempts JSON output, falling back to raw text output if JSON is not supported.
- This module requires `tructl` to be installed on the Ansible controller.

## Examples

```yaml
- name: Inspect a TDF file
  dsp.tructl.inspect:
    src: /data/report.pdf.tdf
  register: tdf_info

- name: Display TDF metadata
  ansible.builtin.debug:
    var: tdf_info.tdf_info

- name: Check TDF attributes before processing
  dsp.tructl.inspect:
    src: /data/sensitive.tdf
  register: tdf_meta

- name: Show raw output if JSON is not available
  ansible.builtin.debug:
    var: tdf_meta.raw_output
  when: tdf_meta.raw_output | length > 0
```

## Return Values

| Key          | Type | Returned                          | Description                                                               |
| ------------ | ---- | --------------------------------- | ------------------------------------------------------------------------- |
| `tdf_info`   | dict | success                           | Parsed TDF metadata including policy, attributes, and key access objects. |
| `raw_output` | str  | when JSON output is not supported | Raw `tructl inspect` output when JSON parsing is not available.           |

## See Also

- [encrypt](encrypt.md) - Encrypt files to TDF format using tructl
- [decrypt](decrypt.md) - Decrypt TDF files using tructl

