import os
import sys
import time
import docker
import requests
import threading
from queue import Queue, Empty
from dotenv import load_dotenv
from log_parser import normalize_log

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/logs/batch")
API_KEY = os.getenv("API_KEY", "")

log_queue = Queue()
monitored = set()


def stream_container_logs(container):
    print("Streaming logs:", container.name)
    try:
        for line in container.logs(stream=True, follow=True, tail=0):
            decoded_line = line.decode("utf-8")
            normalized = normalize_log(container.name, decoded_line)
            log_queue.put(normalized)
    except Exception as e:
        print("Log stream ended:", container.name, e)
    finally:
        monitored.discard(container.id)


def sender_worker():
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    while True:
        batch = []
        start_time = time.time()

        while len(batch) < 50 and (time.time() - start_time) < 2.0:
            try:
                batch.append(log_queue.get(timeout=0.5))
            except Empty:
                continue
        if batch:
            try:
                requests.post(
                    BACKEND_URL, json={"logs": batch}, headers=headers, timeout=5.0
                )
            except Exception as e:
                print("Error sending logs to backend:", e)


def main():
    if not API_KEY:
        print("API_KEY environment variable is missing")
        sys.exit(1)

    # starting the sender thread in the background
    threading.Thread(target=sender_worker, daemon=True).start()

    try:
        client = docker.from_env()
    except Exception as e:
        print("Failed to connect to Docker socket:", e)
        sys.exit(1)

    print("Log Shipper Daemon is searching for active containers!!!")
    while True:
        try:
            for c in client.containers.list():
                is_infra = c.name in [
                    "logging-backend",
                    "mongodb",
                    "otel-collector",
                    "log-shipper",
                    "log_shipper",
                ]
                if not is_infra and c.id not in monitored:
                    monitored.add(c.id)

                    threading.Thread(
                        target=stream_container_logs, args=(c,), daemon=True
                    ).start()
        except Exception as e:
            print("Error listing containers:", e)
        time.sleep(5)


if __name__ == "__main__":
    main()
