FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p logs

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD ["curl", "-f", "http://localhost:8000/health"]|| exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]