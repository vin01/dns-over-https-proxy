FROM python:3

COPY app.py /opt/app/
COPY dnslib /opt/app/dnslib

RUN chmod 555 -R /opt/app && \
    useradd -r app && \
    pip3 install requests

WORKDIR /opt/app/

USER app

CMD python3 app.py
