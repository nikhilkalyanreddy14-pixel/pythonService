# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# We use .dockerignore to ensure .env isn't copied
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
# We use 0.0.0.0 so it's accessible outside the container
CMD ["uvicorn", "App.main:app", "--host", "0.0.0.0", "--port", "8000"]