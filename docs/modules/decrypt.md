# decrypt

Decrypt TDF files using tructl.

## Synopsis

- Decrypts a Trusted Data Format (TDF) file back to its original format using `tructl decrypt`.
- The KAS performs an authorization check before releasing the decryption key.
- This module is idempotent by default and skips decryption if the destination file already exists. Use `force=true` to overwrite existing files.

## Parameters

| Parameter    | Type | Required | Default  | Description                                                                                                                                                 |
| ------------ | ---- | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src`        | str  | yes      |          | Path to the TDF file to decrypt. The file must exist on the Ansible controller.                                                                             |
| `dest`       | str  | no       |          | Output path for the decrypted file. If not specified, `tructl` uses its default output naming convention.                                                   |
| `force`      | bool | no       | `false`  | If set to `true`, overwrite the destination file even if it already exists. If set to `false`, the module will skip decryption when the destination exists. |
| `tructl_bin` | str  | no       | `tructl` | Path to the `tructl` binary.                                                                                                                                |

## Notes

- Authentication must be performed with `virtru.dsp_tructl.auth` before decrypting files.
- The authenticated user must have the required attributes to satisfy the TDF's access policy.
- This module requires `tructl` to be installed on the Ansible controller.

## Examples

```yaml
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
```

## Return Values

| Key    | Type | Returned | Description                 |
| ------ | ---- | -------- | --------------------------- |
| `dest` | str  | success  | Path to the decrypted file. |

## See Also

- [encrypt](encrypt.md) - Encrypt files to TDF format using tructl
- [inspect](inspect.md) - Inspect TDF file metadata
- [auth](auth.md) - Authenticate to DSP platform via tructl

