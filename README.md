# Ansible Collection: virtru.dsp_tructl

The `virtru.dsp_tructl` collection includes modules for managing the Virtru Data Security Platform (DSP) via the `tructl` CLI. It provides idempotent automation for policy management, authentication, encryption, and KAS configuration.

## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.14**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.

## Changelog

See [CHANGELOG.rst](CHANGELOG.rst) for the release history and changes made to this collection.

## Collection Documentation

### Included modules

| Module | Description | Docs |
| ------ | ----------- | ---- |
| [auth](plugins/modules/auth.py) | Authenticate to the DSP platform via `tructl auth login`. | [docs](docs/modules/auth.md) |
| [profile](plugins/modules/profile.py) | Manage tructl CLI profiles for DSP endpoints. | [docs](docs/modules/profile.md) |
| [namespace](plugins/modules/namespace.py) | Manage DSP policy attribute namespaces. | [docs](docs/modules/namespace.md) |
| [attribute](plugins/modules/attribute.py) | Manage DSP policy attributes with anyOf, allOf, and hierarchy rules. | [docs](docs/modules/attribute.md) |
| [subject_mapping](plugins/modules/subject_mapping.py) | Manage subject-to-attribute mappings for ABAC decisions. | [docs](docs/modules/subject_mapping.md) |
| [resource_mapping](plugins/modules/resource_mapping.py) | Manage resource-to-attribute mappings for data tags. | [docs](docs/modules/resource_mapping.md) |
| [kas_registry](plugins/modules/kas_registry.py) | Manage Key Access Server registry entries. | [docs](docs/modules/kas_registry.md) |
| [kas_key](plugins/modules/kas_key.py) | Import and manage KAS registry keys. | [docs](docs/modules/kas_key.md) |
| [kas_grant](plugins/modules/kas_grant.py) | Migrate KAS grants during setup or upgrade. | [docs](docs/modules/kas_grant.md) |
| [encrypt](plugins/modules/encrypt.py) | Encrypt files to Trusted Data Format (TDF). | [docs](docs/modules/encrypt.md) |
| [decrypt](plugins/modules/decrypt.py) | Decrypt TDF files back to their original format. | [docs](docs/modules/decrypt.md) |
| [inspect](plugins/modules/inspect.py) | Inspect TDF file metadata (read-only). | [docs](docs/modules/inspect.md) |

Each module includes full Ansible documentation accessible via `ansible-doc`:

```
ansible-doc virtru.dsp_tructl.encrypt
```

## Installation and Usage

### Requirements

- `tructl` CLI installed on the Ansible controller
- A running DSP platform endpoint
- OIDC client configured in Keycloak for CLI access

### Installing the Collection

Install from Ansible Galaxy:

```bash
ansible-galaxy collection install virtru.dsp_tructl
```

Or include it in a `requirements.yml` file:

```yaml
collections:
  - name: virtru.dsp_tructl
```

Then install with:

```bash
ansible-galaxy collection install -r requirements.yml
```

You can also install directly from the Git repository:

```bash
ansible-galaxy collection install git+https://github.com/gpa7407/ansible-dsp-tructl.git
```

### Example Usage

```yaml
---
- name: Configure DSP policy via tructl
  hosts: localhost
  connection: local
  gather_facts: false

  tasks:
    - name: Setup profile
      virtru.dsp_tructl.profile:
        name: dsp-lab
        endpoint: "https://platform.dsp.lab"
        default: true

    - name: Authenticate
      virtru.dsp_tructl.auth:
        client_id: cli-client

    - name: Create namespace
      virtru.dsp_tructl.namespace:
        name: "https://example.com/attr"

    - name: Create attribute
      virtru.dsp_tructl.attribute:
        namespace: "https://example.com/attr"
        name: classification
        rule: hierarchy
        values: [public, internal, confidential, secret]

    - name: Register KAS
      virtru.dsp_tructl.kas_registry:
        name: primary-kas
        uri: "https://platform.dsp.lab/kas"
```

### Check Mode and Idempotency

All modules support `--check` for dry-run operations. State-based modules query current state via `tructl ... list --json` before making changes, ensuring idempotent operation. Running a playbook twice results in `changed=0` on the second run.

## Contributing to this collection

We welcome contributions. If you find problems, please open an issue or create a PR against the [ansible-dsp-tructl repository](https://github.com/gpa7407/ansible-dsp-tructl).

## Testing

The collection can be validated with:

```bash
# Syntax check all modules
python3 -m py_compile plugins/modules/*.py

# View module documentation
ansible-doc -t module virtru.dsp_tructl.encrypt

# Dry run a playbook
ansible-playbook tests/test_all_modules.yml --check
```

> **Note:** To run the full integration test suite (`test_all_modules.yml`) against a live DSP instance, you must first deploy DSP using the [dsp-self-service](https://github.com/virtru-corp/dsp-self-service) repository. Once the VM is provisioned and DSP is running, execute:
>
> ```bash
> ansible-playbook tests/test_all_modules.yml -i tests/inventory.ini
> ```
>
> You can also run specific module tests using tags (e.g., `--tags encrypt,decrypt`).

## License

GNU General Public License v3.0 or later

See [COPYING](COPYING) to see the full text.

