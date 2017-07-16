FROM python:3.4

RUN apt-get update && apt-get install -qy libfontconfig wget
RUN apt-get install -qy wkhtmltopdf xvfb pdftk

#WORKDIR /tmp
#RUN wget https://downloads.wkhtmltopdf.org/0.12/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz && \
#    tar xJf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz && \
#    cp -r wkhtmltox/* /usr/local/

RUN mkdir -p /usr/src/app/

WORKDIR /usr/src/app/

COPY requirements.txt /usr/src/app/
RUN pip install -U pip
RUN pip install -r requirements.txt

#COPY . /usr/src/app
#COPY ./IOI_Translate/production_settings.py /usr/src/app/IOI_Translate/settings.py

CMD ["./docker-entrypoint.sh"]