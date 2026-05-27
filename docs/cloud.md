---
title: Cloud Remote Access (Experimental)
---

# Cloud Remote Access (Experimental)


Control your printer remotely using cloud-based remote access providers.

> **Note**: Cloud providers are downloaded on-demand when enabled by the user. OctoEverywhere is pinned to a specific upstream commit archive, verified by SHA256, and its Python dependencies are installed from a hash-locked manifest in this repo. See [third-party integration design](design/third_party.md) for details on how external components are managed.

> **Warning**: This feature is experimental. Cloud services consume additional CPU and memory resources which may affect print quality or reliability during active prints. It is recommended to monitor system performance closely.

## Supported Providers

- **none** - Cloud access disabled (default)
- **octoeverywhere** - Remote access via [OctoEverywhere.com](https://octoeverywhere.com)

## OctoEverywhere

- Access your printer remotely from anywhere
- AI print failure detection and notifications
- Webcam streaming and timelapse
- Requires no port forwarding or VPN configuration

### Using firmware-config Web UI (preferred)

Navigate to the [firmware-config](firmware_config.md) web interface, go to the Remote Access section, and select OctoEverywhere under Cloud Provider. This will automatically download the pinned OctoEverywhere source archive, verify its checksum, install its hash-locked Python dependencies, and display the account linking instructions.

### Manual Setup (advanced)

**Step 1:** Download OctoEverywhere (requires internet connection):
```bash
ssh root@<printer-ip>
octoeverywhere-pkg download
```

If the installer reports a source or dependency hash mismatch, stop there and update the firmware package metadata rather than bypassing the check.

**Step 2:** Edit `extended/extended2.cfg`, set the `cloud`:
```ini
[remote_access]
cloud: octoeverywhere
```

**Step 3:** Start the cloud service:
```bash
/etc/init.d/S99cloud restart
```

**Step 4:** Link your account by downloading `octoeverywhere.log` from Mainsail or Fluidd to find the account linking URL. Open the URL in your browser to link your printer to your OctoEverywhere.com account.

**Need help?** Visit [OctoEverywhere Support for Snapmaker U1](https://octoeverywhere.com/s/snapmaker-u1) for assistance.

## Maintainer Lock Refresh

When bumping OctoEverywhere, refresh both the pinned commit archive checksum and the hash-locked dependency manifest together:

```bash
scripts/dev/update_octoeverywhere_lock.sh --commit <upstream-commit> --version <display-version>
```

The script rewrites `octoeverywhere-pkg` and regenerates `requirements.lock`. Review the resulting diff before committing it.

If you prefer GitHub-hosted automation, use the manual `workflow_dispatch` workflow in `.github/workflows/update_octoeverywhere_lock.yaml`. It runs the same script, validates the repo tests, and uploads the refreshed files plus a patch artifact for review.
