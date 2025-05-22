FROM python:3.13.1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .
RUN ls -la *

RUN ls -alF

COPY .env .env
RUN ls -alF

# Copy requirements first for better caching
#COPY ./wheel/google_genai_agents-0.0.2.dev20250204+723246417-py3-none-any.whl .
#RUN pip install google_genai_agents-0.0.2.dev20250204+723246417-py3-none-any.whl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8081

# Command to run the application
CMD ["python", "server.py"]