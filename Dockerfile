FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for psycopg2, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire codebase
COPY . .

# Ensure PYTHONPATH is set so absolute imports work
ENV PYTHONPATH=/app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "dashboard/streamlit_app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
