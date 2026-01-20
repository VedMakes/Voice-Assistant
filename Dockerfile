FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libasound2 \
    portaudio19-dev \
    sox \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code + model
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
