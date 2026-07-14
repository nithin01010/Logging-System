FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY req.txt .
RUN pip install -r req.txt
COPY . .
CMD ["python", "main.py"]

