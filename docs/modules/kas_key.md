# kas_key

Manage KAS registry keys.

## Synopsis

- Imports keys or sets base keys for Key Access Server (KAS) registry entries.
- Key operations are essential for enabling encryption and decryption through the KAS.

## Parameters

| Parameter    | Type | Required | Default  | Description                                                                                                                                                                    |
| ------------ | ---- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `kas_id`     | str  | yes      |          | The KAS registry entry ID to manage keys for.                                                                                                                                  |
| `action`     | str  | yes      |          | The key operation to perform. `import` imports a key file into the KAS registry entry. `base_set` sets the base key for the KAS registry entry. Choices: `import`, `base_set`. |
| `key_file`   | str  | no       |          | Path to the key file on the Ansible controller. Required when `action=import`.                                                                                                 |
| `key_type`   | str  | no       |          | The key type, such as `rsa` or `ec`.                                                                                                                                           |
| `algorithm`  | str  | no       |          | The algorithm identifier, such as `rsa-2048`.                                                                                                                                  |
| `key_id`     | str  | no       |          | The key ID to set as the base key. Required when `action=base_set`.                                                                                                            |
| `tructl_bin` | str  | no       | `tructl` | Path to the `tructl` binary.                                                                                                                                                   |

## Notes

- A KAS registry entry must exist before importing keys. Use `dsp.tructl.kas_registry` first.
- Key import operations are not naturally idempotent. Running the same import twice may result in duplicate keys.
- This module requires `tructl` to be installed on the Ansible controller.

## Examples

```yaml
- name: Import an RSA key into a KAS registry entry
  dsp.tructl.kas_key:
    kas_id: "550e8400-e29b-41d4-a716-446655440000"
    action: import
    key_file: /path/to/public-key.pem
    key_type: rsa
    algorithm: rsa-2048

- name: Set the base key for a KAS registry entry
  dsp.tructl.kas_key:
    kas_id: "550e8400-e29b-41d4-a716-446655440000"
    action: base_set
    key_id: "key-789-abc-012"
```

## Return Values

| Key   | Type | Returned | Description                                        |
| ----- | ---- | -------- | -------------------------------------------------- |
| `key` | dict | always   | Key operation result details.                      |
| `msg` | str  | always   | Result message describing the operation performed. |

## See Also

- [kas_registry](kas_registry.md) - Manage DSP Key Access Server registry entries
- [kas_grant](kas_grant.md) - Migrate KAS grants

