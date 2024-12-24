# Use a lightweight Python base image
FROM python:3.9-slim

# Set a working directory inside the container
WORKDIR /app

# Install system dependencies (useful for certain Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory to the container
COPY . /app/

# Ensure the FAISS index file is included
COPY faiss_index_law /app/faiss_index_law

# Copy the .env file to the container
COPY .env /app/.env

# Expose the port FastAPI will run on
EXPOSE 8000

# Load environment variables from the .env file (this is handled by python-dotenv in your code)
# In case you use a different approach to load variables in your application, make sure to adjust accordingly

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
