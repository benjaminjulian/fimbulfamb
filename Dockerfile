# Use the official Python image as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app and HTML file into the container
COPY app.py .
COPY index.html .

# Expose the port the app will run on
EXPOSE 8080

# Start the Gunicorn server
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
