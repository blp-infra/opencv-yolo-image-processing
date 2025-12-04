# # Use chiselled Python base image
# FROM python:3.12-slim

# # Install UV (fast Python packaging tool)
# RUN pip install uv

# WORKDIR /app

# # Copy project files
# COPY pyproject.toml .
# COPY uv.lock .
# #if it exists

# # Install dependencies using uv (creates venv automatically)
# RUN uv sync --frozen

# # Copy rest of the app
# COPY . .

# # Expose port
# EXPOSE 8000

# # Run FastAPI
# CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# above is good one
# ##******************** with ubuntu python apt**********************
FROM python:3.12

RUN apt-get update && apt-get install -y build-essential libpq-dev

RUN pip install uv

WORKDIR /app

COPY uv.lock .
COPY pyproject.toml .

RUN uv sync --frozen

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# ##******************** with ubuntu python apt**********************
# FROM python:3.12

# RUN apt-get update && apt-get install -y build-essential libpq-dev

# RUN pip install uv

# WORKDIR /app

# COPY uv.lock .
# COPY pyproject.toml .

# RUN uv sync --frozen

# COPY . .

# EXPOSE 8000
# RUN chmod +x start.sh monitor.sh
# CMD ["./start.sh"]

#CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# ##******************** with cron**********************
# FROM python:3.12

# RUN apt-get update && apt-get install -y build-essential libpq-dev cron

# RUN pip install uv

# WORKDIR /app

# COPY uv.lock .
# COPY pyproject.toml .

# RUN uv sync --frozen

# COPY . .

# EXPOSE 8000
# RUN chmod +x start.sh monitor.sh cron.sh
# CMD ["./start.sh"]

#CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#-----------------------------
# ######## suprevisord####
# FROM python:3.12

# RUN apt-get update && apt-get install -y build-essential libpq-dev supervisor

# RUN pip install uv

# WORKDIR /app

# COPY uv.lock .
# COPY pyproject.toml .

# RUN uv sync --frozen
# COPY app.conf /etc/supervisor/conf.d/app.conf
# COPY . .

# EXPOSE 8000
# CMD ["/usr/bin/supervisord", "-n"]
