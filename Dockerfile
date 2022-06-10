FROM debian:bullseye-20220328-slim AS build

ARG PKG_NAME="tinypilot"
ARG PKG_VERSION="0.0.0"
ARG PKG_BUILD_NUMBER="1"
ARG PKG_ARCH="armhf"
ARG PKG_ID="${PKG_NAME}-${PKG_VERSION}-${PKG_BUILD_NUMBER}-${PKG_ARCH}"
RUN set -x && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      dpkg-dev

COPY . /app

WORKDIR /app

RUN echo "${PKG_VERSION}" > VERSION

RUN mkdir -p "/releases/${PKG_ID}"

WORKDIR "/releases/${PKG_ID}"

RUN mkdir -p opt/tinypilot && \
      cp -R /app/* opt/tinypilot/ && \
      rm -rf opt/tinypilot/e2e

RUN mkdir -p DEBIAN

WORKDIR "/releases/${PKG_ID}/DEBIAN"

RUN echo "Package: ${PKG_NAME}" >> control && \
    echo "Version: ${PKG_VERSION}" >> control && \
    echo "Maintainer: TinyPilot Support <support@tinypilotkvm.com>" >> control && \
    echo "Depends: python3, python3-pip, python3-venv, sudo" >> control && \
    echo "Architecture: all" >> control && \
    echo "Homepage: https://tinypilotkvm.com" >> control && \
    echo "Description: Simple, easy-to-use KVM over IP" >> control

RUN echo "#/bin/bash" > preinst && \
    echo "rm -rf /opt/tinypilot" >> preinst && \
    chmod 0555 preinst

RUN echo "#/bin/bash" > postinst && \
    echo "chown -R tinypilot:tinypilot /opt/tinypilot" >> postinst && \
    chmod 0555 postinst

RUN dpkg --build "/releases/${PKG_ID}"

FROM scratch as artifact

COPY --from=build "/releases/*.deb" ./
