# kas_grant

Migrate KAS grants.

## Synopsis

- Runs `tructl migrate kas-grants` to migrate KAS grant configurations.
- This is typically a one-time operation performed during platform setup or upgrade.
- The module always reports `changed=true` as it cannot determine if migration work was performed.

## Parameters

| Parameter     | Type | Required | Default  | Description                                                                                         |
| ------------- | ---- | -------- | -------- | --------------------------------------------------------------------------------------------------- |
| `interactive` | bool | no       | `true`   | Use interactive mode (`-i` flag).                                                                   |
| `commit`      | bool | no       | `true`   | Commit the migration (`-c` flag). When set to `false`, performs a dry run without applying changes. |
| `tructl_bin`  | str  | no       | `tructl` | Path to the `tructl` binary.                                                                        |

## Notes

- This is typically run once after KAS registry and key configuration is complete.
- Use `commit=false` to preview what the migration would do before committing.
- This module requires `tructl` to be installed on the Ansible controller.

## Examples

```yaml
- name: Migrate KAS grants with commit
  dsp.tructl.kas_grant:
    interactive: true
    commit: true

- name: Preview KAS grants migration without committing
  dsp.tructl.kas_grant:
    interactive: true
    commit: false
  register: migration_preview
```

## Return Values

| Key      | Type | Returned | Description                            |
| -------- | ---- | -------- | -------------------------------------- |
| `msg`    | str  | always   | Migration result message.              |
| `stdout` | str  | always   | Raw command output from the migration. |

## See Also

- [kas_registry](kas_registry.md) - Manage DSP Key Access Server registry entries
- [kas_key](kas_key.md) - Manage KAS registry keys

