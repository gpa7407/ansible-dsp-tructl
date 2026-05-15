# resource_mapping

Manage DSP policy resource mappings.

## Synopsis

- Creates, deletes, or lists resource mappings in the DSP platform.
- Resource mappings link data tags and terms to platform attribute values, enabling automatic classification of data based on metadata extracted by the Data Tagging Service.
- This module is idempotent when `state=present` and checks for existing mappings by `attribute_value_id`.

## Parameters

| Parameter            | Type      | Required | Default   | Description                                                                                                                                                                                                                            |
| -------------------- | --------- | -------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `attribute_value_id` | str       | no       |           | The attribute value ID to map to. Required when `state=present`.                                                                                                                                                                       |
| `terms`              | list(str) | no       |           | List of resource mapping terms that will be matched against data tags. Required when `state=present`.                                                                                                                                  |
| `id`                 | str       | no       |           | The resource mapping ID. Required when `state=absent` to identify the mapping to delete.                                                                                                                                               |
| `state`              | str       | no       | `present` | `present` creates the resource mapping if one does not exist for the given `attribute_value_id`. `absent` deletes the resource mapping identified by `id`. `list` returns all resource mappings. Choices: `present`, `absent`, `list`. |
| `tructl_bin`         | str       | no       | `tructl`  | Path to the `tructl` binary.                                                                                                                                                                                                           |

## Notes

- Resource mappings connect the output of the Data Tagging Service to ABAC policy attributes.
- This module requires `tructl` to be installed on the Ansible controller.

## Examples

```yaml
- name: Create a resource mapping for classification
  dsp.tructl.resource_mapping:
    attribute_value_id: "abc-123-def-456"
    terms:
      - "classification:secret"
    state: present

- name: Create a resource mapping with multiple terms
  dsp.tructl.resource_mapping:
    attribute_value_id: "abc-123-def-456"
    terms:
      - "classification:secret"
      - "sensitivity:high"
    state: present

- name: List all resource mappings
  dsp.tructl.resource_mapping:
    state: list
  register: rm_result

- name: Delete a resource mapping by ID
  dsp.tructl.resource_mapping:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
```

## Return Values

| Key                 | Type | Returned                        | Description                    |
| ------------------- | ---- | ------------------------------- | ------------------------------ |
| `resource_mapping`  | dict | when state is present or absent | The resource mapping details.  |
| `resource_mappings` | list | when state is list              | List of all resource mappings. |

## See Also

- [attribute](attribute.md) - Manage DSP policy attributes
- [subject_mapping](subject_mapping.md) - Manage DSP policy subject mappings

