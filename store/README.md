# NOVA Player v1.9 Store preparation

`build_dev_test_bundle.ps1` produces a self-signed bundle for local sideload testing only. It is not a Store submission package.

For a Store submission, reserve the app in Partner Center, then copy the exact Identity Name, Publisher, and Publisher Display Name from the Product identity page into `NOVA_STORE_IDENTITY_NAME`, `NOVA_STORE_PUBLISHER`, and `NOVA_STORE_PUBLISHER_DISPLAY_NAME`. Run `build_store_msix.ps1` to create an unsigned x64 `.msixbundle` with that identity. Microsoft signs Store packages after they pass certification, so this script does not request a production signing certificate.

Microsoft recommends an `.msixupload` file for Windows 10 and later; this project currently produces the requested `.msixbundle`. Run Windows App Certification Kit and test the package on a clean Windows installation before submission. The current build targets x64 only.

See [INSTALL-DEV-TEST.md](INSTALL-DEV-TEST.md) for local testing and [STORE-LAUNCH-CHECKLIST.md](STORE-LAUNCH-CHECKLIST.md) for the remaining Partner Center and release steps. Read `../THIRD_PARTY_NOTICES.md` and the Qt license references before commercial distribution.
