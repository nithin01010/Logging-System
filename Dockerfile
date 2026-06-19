FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m venv venv
RUN pip install --no-cache-dir -r requirements.txt
COPY ..

