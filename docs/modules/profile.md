# profile

Manage tructl CLI profiles.

## Synopsis

- Creates, removes, or lists tructl profiles.
- Profiles store DSP platform endpoint configuration for the tructl CLI.

## Parameters

| Parameter    | Type | Required | Default   | Description                                                                                                                                          |
| ------------ | ---- | -------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`       | str  | yes      |           | The name of the profile to manage.                                                                                                                   |
| `endpoint`   | str  | no       |           | The DSP platform endpoint URL. Required when `state=present`.                                                                                        |
| `default`    | bool | no       | `false`   | Whether to set this profile as the default profile.                                                                                                  |
| `state`      | str  | no       | `present` | `present` creates the profile if it does not exist. `absent` removes the profile. `list` returns all profiles. Choices: `present`, `absent`, `list`. |
| `tructl_bin` | str  | no       | `tructl`  | Path to the tructl binary.                                                                                                                           |

## Notes

- This module requires the tructl CLI to be installed on the target host.
- Check mode is supported.

## Examples

```yaml
- name: Create and set default profile
  dsp.tructl.profile:
    name: dsp-lab
    endpoint: "https://platform.dsp.lab"
    default: true

- name: List all profiles
  dsp.tructl.profile:
    name: unused
    state: list
  register: profiles

- name: Remove a profile
  dsp.tructl.profile:
    name: old-profile
    state: absent
```

## Return Values

| Key        | Type | Returned              | Description           |
| ---------- | ---- | --------------------- | --------------------- |
| `profile`  | dict | when state is present | The profile details.  |
| `profiles` | list | when state is list    | List of all profiles. |

## See Also

- [auth](auth.md) - Authenticate to DSP platform via tructl
- [encrypt](encrypt.md) - Encrypt files to TDF format using tructl

