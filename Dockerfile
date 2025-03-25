# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Set default value for TREATMENT
ENV TREATMENT=True

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages
RUN pip install --no-cache-dir flask

# Make port 8087 available to the world outside this container
EXPOSE 8087

# Run the application
CMD ["python", "app.py"]
