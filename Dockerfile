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

# Pull Botiana from github
RUN git clone https://github.com/rpkish/botiana.git /usr/local/botiana/

# Pull various private configuration files from a private repo
RUN git clone http://<REDACTED>/botiana-settings.git /usr/local/botiana-settings

# Link private configurations to public botiana repo
RUN rm /usr/local/botiana/sa.yaml
RUN ln /usr/local/botiana-settings/sa.yaml /usr/local/botiana/sa.yaml
RUN ln /usr/local/botiana-settings/settings.py /usr/local/botiana/settings.py

# run configuration steps
RUN pip install -r /usr/local/botiana/requirements.txt

# Fire up botiana
ENTRYPOINT cd /usr/local/botiana && ./botiana.py
