FROM mtlynch/debian10-ansible:2.9.13

# We have to reinstall this for some reason?
# https://stackoverflow.com/a/10538412/90388
RUN apt-get update && \
    apt-get remove python-setuptools -y && \
    apt-get install python-setuptools curl -y

# TCP protocol is missing for some reason in test image?
RUN apt-get -o Dpkg::Options::="--force-confmiss" install \
      --reinstall netbase
