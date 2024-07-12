# Use an official Python runtime as a parent image
FROM python:3.11-slim AS base

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only requirements.txt to install dependencies
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Use another stage for final build to keep image size minimal
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the installed packages from the base stage
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copy the rest of the application code
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Argument to specify environment (default to 'dev')
ARG ENVIRONMENT=dev

# Copy environment file based on the ARG value
COPY ./.${ENVIRONMENT}.env .${ENVIRONMENT}.env

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
