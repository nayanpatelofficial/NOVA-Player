# NOVA Player on Linux

This x64 archive is built on Ubuntu 24.04. Extract it, then install for the current user:

```sh
tar -xzf NOVA-Player-v1.10.0-linux-x64.tar.gz
cd NOVA-Player-v1.10.0-linux-x64
bash ./install-linux.sh
```

The installer copies NOVA into `~/.local/opt/nova-player` and adds an application-menu entry. No administrator access is needed. To remove it, run `bash ./uninstall-linux.sh` from this extracted folder.

Qt runtime libraries are bundled. The Linux desktop still needs compatible system multimedia, graphics, and audio libraries; formats depend on the runtime codec components and the distribution. This package is built for x86-64 Linux and is not claimed to work on every distribution. Test it on the target computer before wider deployment.
