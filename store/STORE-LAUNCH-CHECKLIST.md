# NOVA Player Store launch checklist

This repository contains the Windows x64 app, the Store manifest template, generated logo assets, and scripts for a local signed test bundle and an unsigned Store bundle. The Partner Center identity has not been reserved, so the final Store identity cannot yet be filled in or validated.

## Before building the Partner Center package

- Reserve **NOVA Player** under a verified Microsoft Store developer account.
- Copy the exact Identity Name, Publisher, and Publisher Display Name from Partner Center Product identity into the three `NOVA_STORE_*` environment variables.
- Run `store\build_store_msix.ps1`. It creates an unsigned x64 `.msixbundle`; Microsoft signs Store packages that pass certification.
- Run Windows App Certification Kit and install the release package on a clean Windows test machine. Verify launch, media playback, keyboard navigation, and uninstall.
- Finish the listing: screenshots of this build, description, category, age rating, support contact, and a privacy policy URL. Microsoft requires a privacy policy for packaged desktop apps, including apps that do not collect personal data.
- Review `THIRD_PARTY_NOTICES.md` and the exact Qt, FFmpeg, Python, and TinyTag terms/notices for the binary being submitted. Store certification does not replace this license review.
- The current package contains x64 only. Add another architecture only after building and validating a corresponding executable and package.

## Microsoft documentation

- [MSIX Store readiness checklist](https://learn.microsoft.com/en-us/windows/apps/publish/store-readiness-checklist)
- [Package version and identity requirements](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/package-version-numbering?pivots=store-installer-msix)
- [Upload MSIX app packages](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/upload-app-packages?pivots=store-installer-msi-exe)
- [Sign an MSIX package](https://learn.microsoft.com/en-us/windows/msix/package/sign-msix-package-guide)
