# syntax=docker/dockerfile:1.4
# Enable here-documents:
# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/syntax.md#here-documents

FROM debian:bullseye-20220328-slim AS build

ENV DEBIAN_FRONTEND=noninteractive
RUN set -exu && \
    apt-get update && \
    apt-get install --yes --no-install-recommends \
      dpkg-dev \
      devscripts \
      equivs

# Docker populates this value from the --platform argument. See
# https://docs.docker.com/build/building/multi-platform/
ARG TARGETPLATFORM

# The canonical, SemVer-compliant TinyPilot version.
ARG TINYPILOT_VERSION

# The `PKG_VERSION` is the version of the Debian package. Debian uses its own
# versioning scheme, which is not strictly compatible with TinyPilot’s version
# conventions. Therefore, the package version should be a timestamp, formatted
# `YYYYMMDDhhmmss`. That way the package manager always installs the most
# recently built TinyPilot package.
ARG PKG_VERSION

ARG PKG_NAME='tinypilot'
ARG PKG_BUILD_NUMBER='1'

# Docker's platform names don't match Debian's platform names, so we translate
# the platform name from the Docker version to the Debian version and save the
# result to a file so we can re-use it in later stages.
RUN cat | bash <<'EOF'
set -exu
case "${TARGETPLATFORM}" in
  'linux/amd64')
    PKG_ARCH='amd64'
    ;;
  'linux/arm/v7')
    PKG_ARCH='armhf'
    ;;
  *)
    echo "Unrecognized target platform: ${TARGETPLATFORM}" >&2
    exit 1
esac
echo "${PKG_ARCH}" > /tmp/pkg-arch
echo "${PKG_NAME}_${PKG_VERSION}-${PKG_BUILD_NUMBER}_${PKG_ARCH}" > /tmp/pkg-id
EOF

# We ultimately need the directory name to be the package ID, but there's no
# way to specify a dynamic value in Docker's WORKDIR command, so we use a
# placeholder directory name to assemble the Debian package and then rename the
# directory to its package ID name in the final stages of packaging.
WORKDIR /releases/placeholder-pkg-id

COPY ./debian-pkg ./
COPY ./COPYRIGHT ./
COPY ./LICENSE ./
COPY ./README.md ./
COPY ./requirements.txt ./
COPY ./app ./app
COPY ./scripts ./scripts

RUN echo "${TINYPILOT_VERSION}" > VERSION

WORKDIR /releases/placeholder-pkg-id/debian

RUN set -exu && \
    PKG_ARCH="$(cat /tmp/pkg-arch)" && \
    cat >control <<EOF
Source: ${PKG_NAME}
Section: net
Priority: optional
Maintainer: TinyPilot Support <support@tinypilotkvm.com>
Build-Depends:
  debhelper (>= 11),
  dh-virtualenv,
  python3-dev,
  python3-pip,
  python3-venv

Package: ${PKG_NAME}
Architecture: ${PKG_ARCH}
Depends: \${shlibs:Depends},
  \${misc:Depends},
  adduser,
  janus,
  nginx,
  python3,
  sudo,
  ustreamer
Homepage: https://tinypilotkvm.com
Description: Simple, easy-to-use KVM over IP
XBS-Tinypilot-Version: ${TINYPILOT_VERSION}
EOF

# Install build dependencies based on Debian control file.
RUN mk-build-deps \
      --tool 'apt-get --option Debug::pkgProblemResolver=yes --no-install-recommends --yes -qq' \
      --install \
      --remove \
      control

RUN set -exu && \
    cat >changelog <<EOF
tinypilot (${PKG_VERSION}) bullseye; urgency=medium

  * Latest TinyPilot release.

 -- TinyPilot Support <support@tinypilotkvm.com>  $(date '+%a, %d %b %Y %H:%M:%S %z')
EOF

# Rename the placeholder release directory to the final package ID.
WORKDIR /releases
RUN cat | bash <<'EOF'
set -exu
PKG_ID="$(cat /tmp/pkg-id)"
mv placeholder-pkg-id "${PKG_ID}"
cd "${PKG_ID}"
dpkg-buildpackage --build=binary
EOF

FROM scratch as artifact

COPY --from=build /releases/*.deb ./
