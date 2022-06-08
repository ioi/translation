FROM ubuntu:focal

RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections

RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 python3-pip python3-setuptools \
        libfontconfig wkhtmltopdf xvfb libpq-dev ttf-mscorefonts-installer fonts-noto \
        chromium-chromedriver libxcomposite1 libxdamage1 libxtst6 libnss3 libcups2 libxss1 libxrandr2 libasound2 \
        libpangocairo-1.0-0 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 && \
    pip3 install -U pip

COPY binaries/cpdf/cpdf /usr/local/bin/
RUN chmod +x /usr/local/bin/cpdf

COPY trans/static/fonts/ /usr/local/share/fonts/

COPY requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt

RUN python3 -c 'import pyppeteer.command; pyppeteer.command.install()'

COPY docker-entrypoint.sh /root/docker-entrypoint.sh
RUN chmod +x /root/docker-entrypoint.sh

COPY . /usr/src/app
WORKDIR /usr/src/app

ENTRYPOINT ["/root/docker-entrypoint.sh"]
