# encrypt

Encrypt files to TDF format using tructl.

## Synopsis

- Encrypts a file into Trusted Data Format (TDF) using `tructl encrypt`.
- Optionally applies attribute FQNs to control access to the encrypted data.
- This module is idempotent by default and skips encryption if the destination file already exists. Use `force=true` to overwrite existing files.

## Parameters

| Parameter    | Type      | Required | Default  | Description                                                                                                                                                 |
| ------------ | --------- | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src`        | str       | yes      |          | Path to the source file to encrypt. The file must exist on the Ansible controller.                                                                          |
| `dest`       | str       | yes      |          | Output path for the encrypted TDF file.                                                                                                                     |
| `attributes` | list(str) | no       |          | List of attribute FQNs to apply to the TDF. Each attribute is in the format `https://namespace/attr/name/value/val`.                                        |
| `force`      | bool      | no       | `false`  | If set to `true`, overwrite the destination file even if it already exists. If set to `false`, the module will skip encryption when the destination exists. |
| `tructl_bin` | str       | no       | `tructl` | Path to the `tructl` binary.                                                                                                                                |

## Notes

- Authentication must be performed with `dsp.tructl.auth` before encrypting files.
- The TDF format is a standard ZIP archive containing an encrypted payload and manifest.
- This module requires `tructl` to be installed on the Ansible controller.

## Examples

```yaml
- name: Encrypt a file with classification attributes
  dsp.tructl.encrypt:
    src: /data/report.pdf
    dest: /data/report.pdf.tdf
    attributes:
      - "https://example.com/attr/classification/value/secret"

- name: Encrypt a file without attributes
  dsp.tructl.encrypt:
    src: /data/notes.txt
    dest: /data/notes.txt.tdf

- name: Force re-encryption of an existing TDF
  dsp.tructl.encrypt:
    src: /data/report.pdf
    dest: /data/report.pdf.tdf
    force: true
    attributes:
      - "https://example.com/attr/classification/value/confidential"

- name: Encrypt multiple files in a loop
  dsp.tructl.encrypt:
    src: "{{ item }}"
    dest: "{{ item }}.tdf"
    attributes:
      - "https://example.com/attr/classification/value/internal"
  loop:
    - /data/report-q1.pdf
    - /data/report-q2.pdf
```

## Return Values

| Key    | Type | Returned | Description                     |
| ------ | ---- | -------- | ------------------------------- |
| `dest` | str  | success  | Path to the encrypted TDF file. |

## See Also

- [decrypt](decrypt.md) - Decrypt TDF files using tructl
- [inspect](inspect.md) - Inspect TDF file metadata
- [auth](auth.md) - Authenticate to DSP platform via tructl

