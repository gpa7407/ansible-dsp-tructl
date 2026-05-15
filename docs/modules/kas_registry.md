# kas_registry

Manage DSP Key Access Server registry entries.

## Synopsis

- Creates, removes, or lists Key Access Server (KAS) registry entries in the DSP platform.
- KAS servers manage encryption key exchanges and enforce policy through key grant or withhold decisions.
- This module is idempotent when `state=present` and checks for existing entries by `name` or `uri`.

## Parameters

| Parameter    | Type | Required | Default   | Description                                                                                                                                                                                                                               |
| ------------ | ---- | -------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`       | str  | no       |           | The KAS server name. Required when `state=present`.                                                                                                                                                                                       |
| `uri`        | str  | no       |           | The KAS server URI endpoint. Required when `state=present`.                                                                                                                                                                               |
| `id`         | str  | no       |           | The KAS registry entry ID. Required when `state=absent` to identify the entry to delete.                                                                                                                                                  |
| `state`      | str  | no       | `present` | `present` creates the KAS registry entry if one does not exist with the given `name` or `uri`. `absent` deletes the KAS registry entry identified by `id`. `list` returns all KAS registry entries. Choices: `present`, `absent`, `list`. |
| `tructl_bin` | str  | no       | `tructl`  | Path to the `tructl` binary.                                                                                                                                                                                                              |

## Notes

- The KAS is the Policy Enforcement Point (PEP) in the NIST ABAC model.
- After registering a KAS, use `dsp.tructl.kas_key` to import keys.
- This module requires `tructl` to be installed on the Ansible controller.

## Examples

```yaml
- name: Register a KAS server
  dsp.tructl.kas_registry:
    name: primary-kas
    uri: "https://platform.dsp.lab/kas"
    state: present

- name: List all KAS registry entries
  dsp.tructl.kas_registry:
    state: list
  register: kas_result

- name: Remove a KAS registry entry by ID
  dsp.tructl.kas_registry:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
```

## Return Values

| Key              | Type | Returned                        | Description                       |
| ---------------- | ---- | ------------------------------- | --------------------------------- |
| `kas_registry`   | dict | when state is present or absent | The KAS registry entry details.   |
| `kas_registries` | list | when state is list              | List of all KAS registry entries. |

### Sample `kas_registry` return

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "primary-kas",
  "uri": "https://platform.dsp.lab/kas"
}
```

## See Also

- [kas_key](kas_key.md) - Manage KAS registry keys
- [kas_grant](kas_grant.md) - Migrate KAS grants

