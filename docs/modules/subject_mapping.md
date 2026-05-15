# subject_mapping

Manage DSP policy subject mappings.

## Synopsis

- Creates, deletes, or lists subject mappings in the DSP platform.
- Subject mappings link IdP identity attributes to policy attribute values, defining which subjects can perform which actions on data protected by specific attributes.
- This module is idempotent when `state=present` and checks for existing mappings by `attribute_value_id`.

## Parameters

| Parameter                | Type       | Required | Default   | Description                                                                                                                                                                                                                                          |
| ------------------------ | ---------- | -------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `attribute_value_id`     | str        | no       |           | The attribute value ID to map. Required when `state=present`.                                                                                                                                                                                        |
| `actions`                | list(dict) | no       |           | List of action objects for the mapping. Each action is a dictionary with a `standard` key specifying the action type. Common actions include `DECRYPT`, `TRANSMIT`. Required when `state=present`.                                                   |
| `subject_condition_sets` | list(dict) | no       |           | Subject condition set definitions as a list of dictionaries. Each set contains `condition_groups` with boolean operators and conditions. Conditions reference IdP token claims via `subject_external_selector_value`. Required when `state=present`. |
| `id`                     | str        | no       |           | The subject mapping ID. Required when `state=absent` to identify the mapping to delete.                                                                                                                                                              |
| `state`                  | str        | no       | `present` | `present` creates the subject mapping if one does not exist for the given `attribute_value_id`. `absent` deletes the subject mapping identified by `id`. `list` returns all subject mappings. Choices: `present`, `absent`, `list`.                  |
| `tructl_bin`             | str        | no       | `tructl`  | Path to the `tructl` binary.                                                                                                                                                                                                                         |

## Notes

- Subject condition sets have a complex nested structure. It is recommended to define them in a variables file rather than inline in playbooks.
- The module passes `actions` and `subject_condition_sets` as JSON to the tructl CLI.
- This module requires `tructl` to be installed on the Ansible controller.

## Examples

```yaml
- name: Create a subject mapping granting DECRYPT to admins
  dsp.tructl.subject_mapping:
    attribute_value_id: "abc-123-def-456"
    actions:
      - standard: DECRYPT
    subject_condition_sets:
      - condition_groups:
          - boolean_operator: AND
            conditions:
              - subject_external_selector_value: ".realm_access.roles"
                operator: IN
                subject_external_values:
                  - admin
    state: present

- name: List all subject mappings
  dsp.tructl.subject_mapping:
    state: list
  register: sm_result

- name: Delete a subject mapping by ID
  dsp.tructl.subject_mapping:
    id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
```

## Return Values

| Key                | Type | Returned                        | Description                   |
| ------------------ | ---- | ------------------------------- | ----------------------------- |
| `subject_mapping`  | dict | when state is present or absent | The subject mapping details.  |
| `subject_mappings` | list | when state is list              | List of all subject mappings. |

## See Also

- [attribute](attribute.md) - Manage DSP policy attributes
- [resource_mapping](resource_mapping.md) - Manage DSP policy resource mappings

