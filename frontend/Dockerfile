# Use lightweight official Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Start Streamlit application
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]