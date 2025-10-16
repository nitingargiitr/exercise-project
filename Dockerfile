# Use Ubuntu base image with more packages available
FROM ubuntu:22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive
ENV OPENCV_VIDEOIO_PRIORITY_MSMF=0
ENV OPENCV_VIDEOIO_PRIORITY_FFMPEG=1
ENV OPENCV_VIDEOIO_PRIORITY_GSTREAMER=0

# Install Python and essential system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    ffmpeg \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8080

# Start the application
CMD ["./start.sh"]
