"""Build a native Linux tarball or macOS app ZIP with PyInstaller.

PyInstaller is not a cross-compiler. Run this script on the target OS/architecture.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

from nova import __version__


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def copy_runtime_notices(app_folder: Path) -> None:
    if platform.system() == "Darwin":
        notice_folder = app_folder / "Contents" / "Resources" / "Licenses"
        notice_folder.mkdir(parents=True, exist_ok=True)
        notice_target = app_folder / "Contents" / "Resources" / "THIRD_PARTY_NOTICES.md"
    else:
        notice_folder = app_folder / "Licenses"
        notice_folder.mkdir(parents=True, exist_ok=True)
        notice_target = app_folder / "THIRD_PARTY_NOTICES.md"

    for source in (ROOT / "licenses").iterdir():
        if source.is_file():
            shutil.copy2(source, notice_folder / source.name)

    for distribution in __import__("importlib.metadata", fromlist=["distributions"]).distributions():
        name = (distribution.metadata.get("Name") or "").lower().replace("_", "-")
        if not (
            name.startswith("pyside6")
            or name.startswith("shiboken6")
            or name in {"tinytag", "pyinstaller", "pyinstaller-hooks-contrib"}
        ):
            continue
        dist_info = getattr(distribution, "_path", None)
        licenses = Path(dist_info) / "licenses" if dist_info else None
        if not licenses or not licenses.is_dir():
            continue
        target = notice_folder / f"{name}-{distribution.version}"
        shutil.copytree(licenses, target, dirs_exist_ok=True)

    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.is_file():
        shutil.copy2(python_license, notice_folder / "Python-LICENSE.txt")
    shutil.copy2(ROOT / "THIRD_PARTY_NOTICES.md", notice_target)


def run_build() -> Path:
    system = platform.system()
    if system not in {"Linux", "Darwin"}:
        raise SystemExit("Run this script on Linux or macOS. Use build_windows.ps1 on Windows.")

    architecture = platform.machine().lower()
    architecture = {"amd64": "x64", "x86_64": "x64", "arm64": "arm64", "aarch64": "arm64"}.get(
        architecture, architecture
    )
    if system == "Linux" and architecture != "x64":
        raise SystemExit("The Linux release currently targets x64.")

    DIST.mkdir(exist_ok=True)
    add_data = os.pathsep
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "NOVAPlayer",
        "--add-data",
        f"{ROOT / 'assets'}{add_data}assets",
        "--add-data",
        f"{ROOT / 'store' / 'Assets' / 'StoreLogo.png'}{add_data}assets/store-logo.png",
        "--add-data",
        f"{ROOT / 'THIRD_PARTY_NOTICES.md'}{add_data}.",
        str(ROOT / "main.py"),
    ]
    subprocess.run(command, cwd=ROOT, check=True)

    app = DIST / ("NOVAPlayer.app" if system == "Darwin" else "NOVAPlayer")
    if not app.exists():
        raise SystemExit(f"PyInstaller did not create the expected app: {app}")
    copy_runtime_notices(app)

    if system == "Darwin":
        output = DIST / f"NOVA-Player-v{__version__}-macOS-{architecture}.zip"
        subprocess.run(
            ["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(app), str(output)],
            check=True,
        )
    else:
        package = DIST / f"NOVA-Player-v{__version__}-linux-{architecture}"
        if package.exists():
            shutil.rmtree(package)
        package.mkdir()
        shutil.copytree(app, package / "NOVAPlayer")
        for filename in ("install-linux.sh", "uninstall-linux.sh", "README-LINUX.md"):
            shutil.copy2(ROOT / "packaging" / filename, package / filename)
        output = DIST / f"NOVA-Player-v{__version__}-linux-{architecture}.tar.gz"
        with tarfile.open(output, "w:gz") as archive:
            archive.add(package, arcname=package.name)

    print(f"Created {output}")
    return output


if __name__ == "__main__":
    run_build()
