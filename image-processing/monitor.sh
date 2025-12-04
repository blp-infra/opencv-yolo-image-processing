#!/bin/bash

# to  check whether te container is running or not
while true; do
    sleep 10
    pgrep -f "uvicorn main:app" > /dev/null
    if [ $? -ne 0 ]; then
        echo "FastAPI not running, starting..."
        uvicorn main:app --host 0.0.0.0 --port 8000 &
    fi    
    sleep 10
    
done