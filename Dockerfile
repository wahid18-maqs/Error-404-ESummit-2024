# Use a lightweight Python base image
FROM python:3.9-slim

# Set a working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app/

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variables (ensure you set these in Render's dashboard as well)
ENV GEMINI_API_KEY=your_gemini_api_key
ENV HF_API_KEY=your_hugging_face_api_key

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
