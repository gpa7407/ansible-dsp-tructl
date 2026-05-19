================================
DSP Tructl Collection Change Log
================================

.. contents:: Topics

v1.0.0
======

Release Summary
---------------

Initial release of the ``virtru.dsp_tructl`` collection.

Major Changes
-------------

- auth - New module for authenticating to the DSP platform via ``tructl auth login``.
- profile - New module for managing tructl CLI profiles.
- namespace - New module for managing DSP policy attribute namespaces.
- attribute - New module for managing DSP policy attributes with anyOf, allOf, and hierarchy rules.
- subject_mapping - New module for managing DSP subject-to-attribute mappings.
- resource_mapping - New module for managing DSP resource-to-attribute mappings.
- kas_registry - New module for managing KAS registry entries.
- kas_key - New module for importing and managing KAS registry keys.
- kas_grant - New module for migrating KAS grants.
- encrypt - New module for encrypting files to TDF format.
- decrypt - New module for decrypting TDF files.
- inspect - New module for inspecting TDF file metadata.
