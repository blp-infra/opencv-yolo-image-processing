#!/bin/bash

if ! pgrep -f "uvicorn main:app" > /dev/null; then
    echo "$(date) - App down. Restarting..." >> /app/monitor.log
    uvicorn main:app --host 0.0.0.0 --port 8000 &
fi
