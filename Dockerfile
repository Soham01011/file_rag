# Use the official Python 3.13.2 image as the base
FROM python:3.13.2

# Set the working directory in the container
WORKDIR /app

# Copy and install system dependencies (if needed)
RUN apt-get update && apt-get install -y gcc libffi-dev

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies separately to prevent cache issues
RUN pip install --no-cache-dir -r requirements.txt 

# Copy only the 'app' folder into the container
COPY app /app/app
COPY venv /app/venv

# Expose the port FastAPI runs on
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
