#################################
# Botiana Dockerfile for Debian #
#################################

FROM debian
MAINTAINER rpkish

# Configure the basic debian image
RUN apt-get update && apt-get install -y \
    aufs-tools \
    python \
    python-pip \
    python-lxml \
    filters \
    git \
    python-yaml \
 && rm -rf /var/lib/apt/lists/* \
 && pip install BeautifulSoup \
 && pip install beautifulsoup4 

# Install botiana and copy modified settings and dictionaries 
RUN mkdir /usr/local/botiana/
COPY ./botiana.py ./settings.py ./sa.yaml ./keywords.yaml ./requirements.txt /usr/local/botiana/

# run configuration steps
RUN pip install -r /usr/local/botiana/requirements.txt

# Fire up botiana
ENTRYPOINT cd /usr/local/botiana && ./botiana.py
