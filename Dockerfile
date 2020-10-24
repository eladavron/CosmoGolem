FROM gorialis/discord.py

WORKDIR /app

COPY requirements.txt ./

# PIP
RUN python -m pip install -r requirements.txt

COPY . .

CMD ["python", "cqxbot.py"]