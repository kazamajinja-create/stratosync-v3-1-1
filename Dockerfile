FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH="/app/vendor/stratosync_v3core:${PYTHONPATH}"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
