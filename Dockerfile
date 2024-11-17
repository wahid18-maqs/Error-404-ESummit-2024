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

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variables (ensure you set these in Render's dashboard as well)
ENV GEMINI_API_KEY=your_gemini_api_key
ENV HF_API_KEY=your_hugging_face_api_key

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
