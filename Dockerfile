FROM python:3.11-slim
RUN apt update && apt install curl -y && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=1m --timeout=5s --retries=3 CMD curl --silent --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
