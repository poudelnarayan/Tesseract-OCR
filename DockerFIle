# Use Python image as base
FROM python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev

# Set working directory inside container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the FastAPI port
EXPOSE 10000

# Run FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "10000"]
