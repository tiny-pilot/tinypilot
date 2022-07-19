# syntax=docker/dockerfile:1.4
# Enable here-documents:
# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/syntax.md#here-documents

FROM debian:bullseye-20220328-slim AS build

# The canonical TinyPilot version. For TinyPilot Community, this is a git commit
# hash in short form. For TinyPilot Pro, this is a SemVer version.
ARG TINYPILOT_VERSION

# The `PKG_VERSION` is the version of the Debian package. Debian uses its own
# versioning scheme, which is incompatible with TinyPilot Community. Therefore,
# the package version should be a timestamp, formatted `YYYYMMDDhhmmss`. That
# way the package manager always installs the most recently built TinyPilot
# package.
ARG PKG_VERSION

ARG PKG_NAME="tinypilot"
ARG PKG_BUILD_NUMBER="1"
ARG PKG_ARCH="armhf"
ARG PKG_ID="${PKG_NAME}-${PKG_VERSION}-${PKG_BUILD_NUMBER}-${PKG_ARCH}"

RUN set -x && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      dpkg-dev

RUN mkdir -p "/releases/${PKG_ID}"

WORKDIR "/releases/${PKG_ID}"

RUN mkdir -p opt/tinypilot
COPY . ./opt/tinypilot/

RUN echo "${TINYPILOT_VERSION}" > opt/tinypilot/VERSION

RUN mkdir -p DEBIAN

WORKDIR "/releases/${PKG_ID}/DEBIAN"

RUN echo "Package: ${PKG_NAME}" >> control && \
    echo "Version: ${PKG_VERSION}" >> control && \
    echo "Maintainer: TinyPilot Support <support@tinypilotkvm.com>" >> control && \
    echo "Depends: python3, python3-pip, python3-venv, sudo" >> control && \
    echo "Architecture: all" >> control && \
    echo "Homepage: https://tinypilotkvm.com" >> control && \
    echo "Description: Simple, easy-to-use KVM over IP" >> control

RUN cat > preinst <<EOF
#!/bin/bash

# If a .git directory exists, the previous version was installed with the legacy
# installer, so wipe the install location and the installer directory clean.
if [[ -d /opt/tinypilot/.git ]]; then
  rm -rf /opt/tinypilot /opt/tinypilot-updater
fi
EOF
RUN chmod 0555 preinst

RUN echo "#!/bin/bash" > postinst && \
    echo "chown -R tinypilot:tinypilot /opt/tinypilot" >> postinst && \
    chmod 0555 postinst

RUN cat > prerm <<EOF
#!/bin/bash

# Exit script on first failure.
set -e

cd /opt/tinypilot
rm -rf venv
find . \
  -type f \
  -name *.pyc \
  -delete \
  -or \
  -type d \
  -name __pycache__ \
  -delete
EOF
RUN chmod 0555 prerm

RUN dpkg --build "/releases/${PKG_ID}"

FROM scratch as artifact

COPY --from=build "/releases/*.deb" ./
