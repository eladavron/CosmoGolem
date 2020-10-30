FROM gorialis/discord.py

WORKDIR /app

COPY requirements.txt ./
COPY . .

# PIP
RUN python -m pip install -r requirements.txt

CMD ["python", "CQXBot/cqxbot.py"]