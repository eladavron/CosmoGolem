FROM gorialis/discord.py

WORKDIR /

COPY requirements.txt ./
COPY CQXBot app
COPY data data

VOLUME [ "/data" ]

# PIP
RUN python -m pip install -r requirements.txt

ENV CQXBOT_DATAPATH="/data"

WORKDIR /app
CMD ["python", "cqxbot.py"]