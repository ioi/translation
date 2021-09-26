FROM ubuntu:focal

RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections

RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 python3-pip python3-setuptools \
        libfontconfig wkhtmltopdf xvfb libpq-dev ttf-mscorefonts-installer fonts-takao-pgothic && \
    pip3 install -U pip

COPY binaries/cpdf/cpdf /usr/local/bin/
RUN chmod +x /usr/local/bin/cpdf

COPY trans/static/fonts/ /usr/local/share/fonts/

COPY requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt

COPY docker-entrypoint.sh /root/docker-entrypoint.sh
RUN chmod +x /root/docker-entrypoint.sh

COPY . /usr/src/app
WORKDIR /usr/src/app

ENTRYPOINT ["/root/docker-entrypoint.sh"]
