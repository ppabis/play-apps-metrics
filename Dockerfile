FROM python:3.11-bookworm

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt\
 && rm /tmp/requirements.txt

WORKDIR /app
COPY src /app/src/
COPY main.py /app/

ENTRYPOINT [ "/usr/local/bin/python3", "-u" ]

CMD [ "main.py" ]