# attribute

Manage DSP policy attributes.

## Synopsis

- Creates, deactivates, or lists policy attributes in the DSP platform.
- Attributes belong to namespaces and define access control dimensions.
- Use this module to automate attribute lifecycle management as part of DSP policy configuration.

## Parameters

| Parameter    | Type | Required | Default   | Description                                                                                                                                                             |
| ------------ | ---- | -------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `namespace`  | str  | yes      |           | The namespace name or ID the attribute belongs to.                                                                                                                      |
| `name`       | str  | yes      |           | The attribute name (e.g., `classification`).                                                                                                                            |
| `rule`       | str  | no       |           | The attribute rule type that governs how attribute values are evaluated during access decisions. Choices: `anyOf`, `allOf`, `hierarchy`. Required when `state=present`. |
| `values`     | list | no       |           | List of attribute values to assign to the attribute. Required when `state=present`.                                                                                     |
| `state`      | str  | no       | `present` | `present` creates the attribute if it does not exist. `absent` deactivates the attribute. `list` returns all attributes. Choices: `present`, `absent`, `list`.          |
| `tructl_bin` | str  | no       | `tructl`  | Path to the tructl binary.                                                                                                                                              |

## Notes

- This module requires the `tructl` CLI to be installed and accessible on the target host.
- Check mode is supported for all states.
- When `state=absent`, the attribute is deactivated rather than permanently deleted.

## Examples

```yaml
- name: Create a classification attribute with hierarchy rule
  dsp.tructl.attribute:
    namespace: "https://example.com/attr"
    name: classification
    rule: hierarchy
    values:
      - public
      - internal
      - confidential
      - secret
    state: present

- name: Create a department attribute with anyOf rule
  dsp.tructl.attribute:
    namespace: "https://example.com/attr"
    name: department
    rule: anyOf
    values:
      - engineering
      - finance
      - hr
    state: present

- name: Deactivate an attribute
  dsp.tructl.attribute:
    namespace: "https://example.com/attr"
    name: classification
    state: absent

- name: List all attributes
  dsp.tructl.attribute:
    namespace: unused
    name: unused
    state: list
  register: attr_result
```

## Return Values

| Key          | Type | Returned                        | Description                                             |
| ------------ | ---- | ------------------------------- | ------------------------------------------------------- |
| `attribute`  | dict | when state is present or absent | The attribute details returned from the DSP platform.   |
| `attributes` | list | when state is list              | List of all attributes retrieved from the DSP platform. |

### Sample `attribute` return

```json
{
  "id": "b4e3c2a1-5678-4def-9abc-1234567890ab",
  "name": "classification",
  "rule": "hierarchy",
  "namespace": {
    "id": "a1b2c3d4-5678-4def-9abc-abcdef123456",
    "name": "https://example.com/attr"
  },
  "values": [
    { "value": "public" },
    { "value": "internal" },
    { "value": "confidential" },
    { "value": "secret" }
  ],
  "active": true
}
```

## See Also

- [namespace](namespace.md) - Manage DSP policy attribute namespaces
- [subject_mapping](subject_mapping.md) - Manage DSP policy subject mappings

