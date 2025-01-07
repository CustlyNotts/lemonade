#!/bin/bash

# Configure variables
CPU_THRESHOLD=80
CHECK_INTERVAL=60 # Time in seconds
SERVICE_NAME="laravel_service_name" # Replace with Laravel service name (e.g., php-fpm, nginx, etc.)
RESTART_COMMAND="sudo systemctl restart $SERVICE_NAME" # Command to restart the service

while true; do
  # Get CPU usage
  cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')

  # Check if CPU usage outshoots the threshold
  if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
    echo "$(date): CPU usage exceeded $CPU_THRESHOLD% ($cpu_usage%). Restarting $SERVICE_NAME..."

    # Restart the service
    if eval "$RESTART_COMMAND"; then # Execute the command
        echo "$(date): $SERVICE_NAME restarted successfully."
        sleep 10
    else
        echo "$(date): ERROR: Failed to restart $SERVICE_NAME."
    fi
  fi

  sleep $CHECK_INTERVAL
done
