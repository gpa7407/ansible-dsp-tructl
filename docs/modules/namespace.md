# namespace

Manage DSP policy attribute namespaces.

## Synopsis

- Creates, deactivates, or lists attribute namespaces in the DSP platform.
- Uses the `tructl` CLI to interact with the DSP policy service.

## Parameters

| Parameter    | Type | Required | Default   | Description                                                                                                                                                    |
| ------------ | ---- | -------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`       | str  | yes      |           | The namespace name (e.g., `https://example.com/attr`). Required for all states, though ignored when `state=list`.                                              |
| `state`      | str  | no       | `present` | `present` creates the namespace if it does not exist. `absent` deactivates the namespace. `list` returns all namespaces. Choices: `present`, `absent`, `list`. |
| `tructl_bin` | str  | no       | `tructl`  | Path to the `tructl` binary.                                                                                                                                   |

## Notes

- This module requires the `tructl` CLI to be installed and configured on the target host.
- Check mode is supported for `present` and `absent` states.

## Examples

```yaml
- name: Create a namespace
  dsp.tructl.namespace:
    name: "https://example.com/attr"
    state: present

- name: List all namespaces
  dsp.tructl.namespace:
    name: unused
    state: list
  register: ns_result

- name: Deactivate a namespace
  dsp.tructl.namespace:
    name: "https://example.com/attr"
    state: absent
```

## Return Values

| Key          | Type | Returned                        | Description                                            |
| ------------ | ---- | ------------------------------- | ------------------------------------------------------ |
| `namespace`  | dict | when state is present or absent | The namespace details returned from the DSP platform.  |
| `namespaces` | list | when state is list              | List of all namespaces registered in the DSP platform. |

### Sample `namespace` return

```json
{
  "id": "e2e4d5f6-7890-1234-abcd-ef0123456789",
  "name": "https://example.com/attr",
  "active": true,
  "fqn": "https://example.com/attr"
}
```

## See Also

- [attribute](attribute.md) - Manage DSP policy attributes

