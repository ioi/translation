FROM ubuntu:xenial-20170710

RUN apt-get -yq update && \
    apt-get -yq install apt-transport-https

RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections
RUN apt-get -yq install python3 python3-pip libfontconfig wkhtmltopdf xvfb \
        libpq-dev ttf-mscorefonts-installer fonts-takao-pgothic && \
    pip3 install -U pip

COPY binaries/cpdf/cpdf /usr/bin/
RUN chmod +x /usr/bin/cpdf

COPY trans/static/fonts/IRANSans/ttf/* /usr/share/fonts/
COPY trans/static/fonts/SourceSansPro/ttf/* /usr/share/fonts/
COPY trans/static/fonts/Korean/* /usr/share/fonts/
COPY trans/static/fonts/Thai/* /usr/share/fonts/
COPY trans/static/fonts/Taiwan/* /usr/share/fonts/

COPY requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt

COPY docker-entrypoint.sh /root/docker-entrypoint.sh
RUN chmod +x /root/docker-entrypoint.sh

COPY . /usr/src/app
WORKDIR /usr/src/app

ENTRYPOINT ["/root/docker-entrypoint.sh"]
