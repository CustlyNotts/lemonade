import os
import time
import requests
from prometheus_client import start_http_server, Gauge

## Environment variables
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "guest")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT", "15672")  ## Management plugin port
EXPORTER_PORT = int(os.environ.get("EXPORTER_PORT", "9100"))

## Prometheus metrics
rabbitmq_individual_queue_messages = Gauge(
    "rabbitmq_individual_queue_messages",
    "Total count of messages in a queue",
    ["host", "vhost", "name"],
)
rabbitmq_individual_queue_messages_ready = Gauge(
    "rabbitmq_individual_queue_messages_ready",
    "Count of ready messages in a queue",
    ["host", "vhost", "name"],
)
rabbitmq_individual_queue_messages_unacknowledged = Gauge(
    "rabbitmq_individual_queue_messages_unacknowledged",
    "Count of unacknowledged messages in a queue",
    ["host", "vhost", "name"],
)

def fetch_queue_metrics():
    url = f"http://{RABBITMQ_HOST}:{RABBITMQ_PORT}/api/queues/%2F"  ## Retrieve all queues from all vhosts
    auth = (RABBITMQ_USER, RABBITMQ_PASSWORD)
    try:
        response = requests.get(url, auth=auth, timeout=10)
        response.raise_for_status()  ## Raise HTTPError for bad responses
        queues = response.json()

        for queue in queues:
            vhost = queue.get('vhost', 'default')  ## Handle cases where vhost might be missing
            name = queue["name"]
            messages = queue.get("messages", 0)
            messages_ready = queue.get("messages_ready", 0)
            messages_unacknowledged = queue.get("messages_unacknowledged", 0)

            rabbitmq_individual_queue_messages.labels(RABBITMQ_HOST, vhost, name).set(messages)
            rabbitmq_individual_queue_messages_ready.labels(RABBITMQ_HOST, vhost, name).set(messages_ready)
            rabbitmq_individual_queue_messages_unacknowledged.labels(RABBITMQ_HOST, vhost, name).set(messages_unacknowledged)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching RabbitMQ metrics: {e}")

def main():
    start_http_server(EXPORTER_PORT)
    print(f"Starting Prometheus exporter on port {EXPORTER_PORT}")
    while True:
        fetch_queue_metrics()
        time.sleep(10)  ## Scrape interval can be adjusted here

if __name__ == "__main__":
    main()
