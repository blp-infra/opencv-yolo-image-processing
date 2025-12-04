# Use your existing image as the base
FROM qms_6.3:Abc

# Set working directory
WORKDIR /app

COPY requirements.txt /app/requirements.txt
# Copy your Python script into the container
COPY script.py /app/script.py

# Install Python if not present OR install required packages
RUN apt-get update && apt-get install -y python3
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the required port
EXPOSE 8000 8554 8888


# Set entrypoint to run the python script
ENTRYPOINT ["python3", "/app/script.py"]
