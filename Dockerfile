# Use a Python version compatible with your dependencies
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements.txt to leverage Docker's caching
COPY requirements.txt /app/

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Environment variables for secrets
ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV HF_API_KEY=${HF_API_KEY}

# Define the command to run your app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
