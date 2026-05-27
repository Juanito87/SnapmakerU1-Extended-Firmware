FROM debian:trixie@sha256:4ae67669760b807c19f23902a3fd7c121a6a70cf2ae709035674b23e712e4d62

ARG TARGETARCH=amd64
ARG BUILD_ESSENTIAL_VERSION=12.12
ARG CMAKE_VERSION=3.31.6-2
ARG PKG_CONFIG_VERSION=1.8.1-4
ARG SQUASHFS_TOOLS_VERSION=1:4.6.1-1
ARG GIT_VERSION=1:2.47.3-0+deb13u1
ARG BC_VERSION=1.07.1-4
ARG FLEX_VERSION=2.6.4-8.2+b4
ARG BISON_VERSION=2:3.8.2+dfsg-1+b2
ARG CA_CERTIFICATES_VERSION=20250419
ARG LIBSSL_DEV_VERSION=3.5.6-1~deb13u1
ARG DOS2UNIX_VERSION=7.5.2-1
ARG SUDO_VERSION=1.9.16p2-3+deb13u2
ARG SSHPASS_VERSION=1.10-0.1
ARG UNZIP_VERSION=6.0-29
ARG WGET_VERSION=1.25.0-2
ARG FILE_VERSION=1:5.46-5
ARG GXX_AARCH64_VERSION=4:14.2.0-1
ARG GCC_AARCH64_VERSION=4:14.2.0-1
ARG U_BOOT_TOOLS_VERSION=2025.01-3
ARG DEVICE_TREE_COMPILER_VERSION=1.7.2-2+b1
ARG GOLANG_GO_VERSION=2:1.24~2
ARG FFMPEG_VERSION=7:7.1.4-0+deb13u1
ARG CCACHE_VERSION=4.11.2-2
ARG LIBSSL_DEV_ARM64_VERSION=3.5.6-1~deb13u1

RUN set -eux; \
    detected_arch="$(dpkg --print-architecture)"; \
    case "${detected_arch}" in \
      amd64) \
        dpkg --add-architecture arm64; \
        foreign_ssl_package="libssl-dev:arm64=${LIBSSL_DEV_ARM64_VERSION}*"; \
        ;; \
      arm64) \
        foreign_ssl_package=""; \
        ;; \
      *) \
        echo "Unsupported Debian architecture: ${detected_arch} (TARGETARCH=${TARGETARCH})" >&2; \
        exit 1; \
        ;; \
    esac; \
    apt-get update -y; \
    apt_packages=" \
      build-essential=${BUILD_ESSENTIAL_VERSION}* \
      cmake=${CMAKE_VERSION}* \
      pkg-config=${PKG_CONFIG_VERSION}* \
      squashfs-tools=${SQUASHFS_TOOLS_VERSION}* \
      git=${GIT_VERSION}* \
      bc=${BC_VERSION}* \
      flex=${FLEX_VERSION}* \
      bison=${BISON_VERSION}* \
      ca-certificates=${CA_CERTIFICATES_VERSION}* \
      libssl-dev=${LIBSSL_DEV_VERSION}* \
      dos2unix=${DOS2UNIX_VERSION}* \
      sudo=${SUDO_VERSION}* \
      sshpass=${SSHPASS_VERSION}* \
      unzip=${UNZIP_VERSION}* \
      wget=${WGET_VERSION}* \
      file=${FILE_VERSION}* \
      g++-aarch64-linux-gnu=${GXX_AARCH64_VERSION}* \
      gcc-aarch64-linux-gnu=${GCC_AARCH64_VERSION}* \
      u-boot-tools=${U_BOOT_TOOLS_VERSION}* \
      device-tree-compiler=${DEVICE_TREE_COMPILER_VERSION}* \
      golang-go=${GOLANG_GO_VERSION}* \
      ffmpeg=${FFMPEG_VERSION}* \
      ccache=${CCACHE_VERSION}* \
    "; \
    if [ -n "${foreign_ssl_package}" ]; then \
      apt_packages="${apt_packages} ${foreign_ssl_package}"; \
    fi; \
    apt-get install -y --no-install-recommends ${apt_packages}; \
    git config --global --add safe.directory '*'; \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/lib/ccache:${PATH}"
ENV CCACHE_MAXSIZE="512M"

WORKDIR /workspace
