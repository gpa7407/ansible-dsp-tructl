# auth

Authenticate to DSP platform via tructl.

## Synopsis

- Performs authentication to the DSP platform using `tructl auth login`.
- This should be run before any other tructl operations that require authentication.
- Authentication tokens are ephemeral so this module always reports `changed=true`.

## Parameters

| Parameter       | Type | Required | Default  | Description                                                                                                                                                                       |
| --------------- | ---- | -------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `client_id`     | str  | yes      |          | The OIDC client ID to authenticate with. For public clients such as `cli-client`, no secret is required.                                                                          |
| `client_secret` | str  | no       |          | The OIDC client secret for confidential clients. Not required for public clients. When specified, it is recommended to set `no_log=true` on the task to prevent credential leaks. |
| `tructl_bin`    | str  | no       | `tructl` | Path to the `tructl` binary.                                                                                                                                                      |

## Notes

- Always set `no_log=true` when using `client_secret` to prevent credential exposure in logs.
- This module requires `tructl` to be installed on the Ansible controller.
- A profile should be configured with `dsp.tructl.profile` before authenticating.

## Examples

```yaml
- name: Authenticate with a public client
  dsp.tructl.auth:
    client_id: cli-client

- name: Authenticate with a confidential client
  dsp.tructl.auth:
    client_id: my-service
    client_secret: "{{ vault_client_secret }}"
  no_log: true

- name: Authenticate using a custom tructl binary path
  dsp.tructl.auth:
    client_id: cli-client
    tructl_bin: /usr/local/bin/tructl
```

## Return Values

| Key   | Type | Returned | Description                    |
| ----- | ---- | -------- | ------------------------------ |
| `msg` | str  | always   | Authentication result message. |

## See Also

- [profile](profile.md) - Manage tructl CLI profiles

