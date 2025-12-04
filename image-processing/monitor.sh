# #!/bin/bash

# # to  check whether te container is running or not
# while true; do
#     sleep 10
#     pgrep -f "uvicorn main:app" > /dev/null
#     if [ $? -ne 0 ]; then
#         echo "FastAPI not running, starting..."
#         /home/manudev/Documents/Codes/blp-industry-ai/opencv-yolo-image-processing/image-processing/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 &
#     fi    
#     sleep 10
    
# done
# 

#!/bin/bash

CONTAINER_NAME="whileloop"   # <-- change this to your container name

while true; do
    sleep 10

    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -w "$CONTAINER_NAME" > /dev/null; then
        echo "$(date): $CONTAINER_NAME is NOT running. Restarting..."
        docker start "$CONTAINER_NAME"
    else
        echo "$(date): $CONTAINER_NAME is running."
    fi

done
