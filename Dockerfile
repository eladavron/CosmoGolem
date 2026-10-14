FROM python:3.12-slim

WORKDIR /

COPY requirements.txt ./
COPY CosmoGolem app
COPY data/settings.template.json data/

VOLUME [ "/data" ]

# PIP
RUN python -m pip install --no-cache-dir -r requirements.txt

ENV CQXBOT_DATAPATH="/data"

WORKDIR /app
CMD ["python", "cqxbot.py"]