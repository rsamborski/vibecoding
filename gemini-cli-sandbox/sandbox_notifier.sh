#!/bin/bash

# Define your container name here
CONTAINER=$(docker ps | grep "gemini-cli" | awk '{print $1}')

echo "Listening for notifications from $CONTAINER..."

# Listen for specific strings and trigger a local bell
docker logs --tail 0 -f "$CONTAINER" 2>&1 | grep --line-buffered -E "Answer Questions|Action Required" | while read -r line; do
    echo -e "\a🔔 Notification intercepted at $(date)"
done
