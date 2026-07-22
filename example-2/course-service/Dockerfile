# Use the official lightweight Python 3.12 image as the base image.
FROM python:3.12-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file into the container.
COPY requirements.txt .

# Install the required Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container.
COPY . .

# Create a non-root user for running the application.
RUN useradd -m appuser

# Switch to the non-root user.
USER appuser

# Document that the application listens on port 8000.
EXPOSE 8000

# Start the FastAPI application using Uvicorn.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]