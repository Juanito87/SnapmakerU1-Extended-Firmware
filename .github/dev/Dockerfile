FROM debian:trixie@sha256:4ae67669760b807c19f23902a3fd7c121a6a70cf2ae709035674b23e712e4d62

RUN dpkg --add-architecture arm64 && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
      # Core build tools.
      build-essential=12.12 \
      cmake=3.31.6-2 \
      pkg-config=1.8.1-4 \
      squashfs-tools=1:4.6.1-1 \
      git=1:2.47.3-0+deb13u1 \
      bc=1.07.1-4 \
      flex=2.6.4-8.2+b4 \
      bison=2:3.8.2+dfsg-1+b2 \
      ca-certificates=20250419 \
      libssl-dev=3.5.6-1~deb13u1 \
      dos2unix=7.5.2-1 \
      sudo=1.9.16p2-3+deb13u2 \
      sshpass=1.10-0.1 \
      unzip=6.0-29 \
      wget=1.25.0-2 \
      file=1:5.46-5 \
      # Cross-compilation and firmware packaging.
      g++-aarch64-linux-gnu=4:14.2.0-1 \
      gcc-aarch64-linux-gnu=4:14.2.0-1 \
      u-boot-tools=2025.01-3 \
      # Language/runtime tooling used by build helpers.
      golang-go=2:1.24~2 \
      ffmpeg=7:7.1.4-0+deb13u1 \
      ccache=4.11.2-2 \
      libssl-dev:arm64=3.5.6-1~deb13u1 \
    && git config --global --add safe.directory '*' \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/lib/ccache:${PATH}"
ENV CCACHE_MAXSIZE="512M"

WORKDIR /workspace
