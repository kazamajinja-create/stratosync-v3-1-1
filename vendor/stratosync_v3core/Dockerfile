FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV AUDIT_LOG_PATH=data/audit_log.jsonl
ENV STATE_DB_PATH=data/state_db.json
ENV ADMIN_TOKEN=CHANGE_ME

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
