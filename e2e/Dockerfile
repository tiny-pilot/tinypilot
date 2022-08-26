FROM geerlingguy/docker-debian10-ansible

RUN apt-get update && \
    apt-get install \
      -y \
      curl \
      git

# TCP protocol is missing for some reason in test image, so we need to
# reinstall it.
RUN apt-get -o Dpkg::Options::="--force-confmiss" install \
      --reinstall netbase
