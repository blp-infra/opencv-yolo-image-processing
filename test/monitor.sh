#!/bin/bash

# List of container names to monitor
CONTAINERS=("latest" "def" "AbC")  # <-- update names here

while true; do
    sleep 10

    for CONTAINER in "${CONTAINERS[@]}"; do

        # Check if container is running
        if ! docker ps --format '{{.Names}}' | grep -w "$CONTAINER" > /dev/null; then
            echo "$(date): $CONTAINER is NOT running. Restarting..."
            docker start "$CONTAINER"
        else
            echo "$(date): $CONTAINER is running."
        fi

    done

done
