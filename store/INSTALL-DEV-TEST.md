# Install the local NOVA Player test build

The .msixbundle from dist\dev-test is signed with a temporary, self-signed developer certificate. It is only for sideload testing and must not be uploaded to Partner Center or shared as a public release.

1. Extract the source ZIP and build dist\dev-test\NOVAPlayer-v1.9.0-DevTest.msixbundle using store\build_dev_test_bundle.ps1, or copy the bundle and NOVAPlayer-DevTest.cer from the generated dist\dev-test folder.
2. Place both generated files in the same folder as store\install_dev_test.ps1.
3. Open PowerShell as Administrator in that folder. App Installer checks the Local Computer > Trusted People certificate store; importing this certificate only for the current user is not enough.
4. Run Set-ExecutionPolicy -Scope Process Bypass, then .\install_dev_test.ps1. The script trusts the test certificate in Local Computer > Trusted People and installs the package.
5. When finished, open PowerShell as Administrator in the same folder and run .\remove_dev_test.ps1 to uninstall the test app and remove the matching certificate from both the machine and current-user stores.

Trusting this self-signed certificate allows packages signed by it to install on this machine. Remove the certificate after testing. The install script is deliberately user-run; this project did not install the certificate or MSIX on the machine used to build it. The package was packed, signed, and successfully unpacked by MakeAppx for structural validation.
