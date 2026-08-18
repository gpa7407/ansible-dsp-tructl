===================================
DSP Tructl Collection Release Notes
===================================

.. contents:: Topics

v1.1.0
======

Release Summary
---------------

Adds DSP 2.0.7 compatibility. Policy modules now resolve namespace names/FQNs
to UUIDs (required by tructl on 2.0.7), and DSP version compatibility is
documented in the README.

Minor Changes
-------------

- attribute, namespace_key, obligation - Resolve the namespace to a UUID before invoking tructl so playbooks can keep passing namespace names on DSP 2.0.7, which now requires namespace IDs.
- tructl_common - Add ``is_uuid()`` and ``TructlRunner.resolve_namespace_id()`` to resolve a namespace name/FQN to its UUID.

Deprecated Features
-------------------

- provision - Not supported on DSP 2.0.7+, where ``tructl provision`` is a deprecated no-op; compose the individual policy modules instead.

Bugfixes
--------

- Module documentation now renders on Ansible Galaxy / Automation Hub - document the shared connection options (host, tls_no_verify, client_creds) via a doc fragment, fix the author format, and correct the attribute 'rule' choices to match the argument spec.
- attribute - Fix attribute creation on DSP 2.0.7, which rejected the namespace name with "namespace_id - must be a valid UUID".

v1.0.0
======

Release Summary
---------------

Initial release of the ``virtru.dsp_tructl`` collection.

Major Changes
-------------

- attribute - New module for managing DSP policy attributes with anyOf, allOf, and hierarchy rules.
- auth - New module for authenticating to the DSP platform via ``tructl auth login``.
- decrypt - New module for decrypting TDF files.
- encrypt - New module for encrypting files to TDF format.
- inspect - New module for inspecting TDF file metadata.
- kas_grant - New module for migrating KAS grants.
- kas_key - New module for importing and managing KAS registry keys.
- kas_registry - New module for managing KAS registry entries.
- namespace - New module for managing DSP policy attribute namespaces.
- profile - New module for managing tructl CLI profiles.
- resource_mapping - New module for managing DSP resource-to-attribute mappings.
- subject_mapping - New module for managing DSP subject-to-attribute mappings.
