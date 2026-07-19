FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --system --create-home appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
RUN chown -R appuser:appuser /app

USER appuser
EXPOSE 8080
CMD ["sh", "-c", "python -m app.bootstrap && exec gunicorn --bind 0.0.0.0:8080 --workers 2 --access-logfile - --error-logfile - 'app.app:create_app()'"]
