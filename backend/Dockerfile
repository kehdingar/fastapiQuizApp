FROM python:3.10

WORKDIR /app

RUN apt update && \
    apt install -y postgresql-client

# Copy the requirements file
COPY requirements.txt ./

# Upgrade pip
RUN pip install --upgrade pip

RUN pip install --upgrade alembic

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port 8000 for the FastAPI application
EXPOSE 8000

CMD ["./prestart.sh", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
