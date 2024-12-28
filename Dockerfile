FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r /requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "bot.py"]
