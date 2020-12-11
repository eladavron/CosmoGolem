FROM gorialis/discord.py

WORKDIR /app

COPY requirements.txt ./
COPY CQXBot CQXBot
COPY data data

VOLUME [ "/data" ]

# PIP
RUN python -m pip install -r requirements.txt

ENV CQXBOT_DATAPATH="/data"

CMD ["python", "CQXBot/cqxbot.py"]