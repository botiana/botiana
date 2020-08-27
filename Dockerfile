#################################
# Botiana Dockerfile for Alpine #
#################################
FROM arm64v8/alpine
MAINTAINER rpkish

# Build deps
RUN apk update \
    && apk add --virtual build-dependencies build-base py3-lxml libxml2-dev libxslt-dev python3 py3-pip python3-dev

# run configuration steps
COPY ./requirements.txt /usr/local/botiana/
RUN pip install -r /usr/local/botiana/requirements.txt
 
# Install botiana and copy modified settings and dictionaries 
COPY ./botiana.py ./settings.py ./common.py ./keywords.py ./legacy_modules.py  \
     ./message_router.py ./settings.py ./slack_commands.py /usr/local/botiana/
COPY data/data.yaml /usr/local/botiana/data/


# Fire up botiana
WORKDIR /usr/local/botiana
CMD /usr/bin/python3 -u ./botiana.py
