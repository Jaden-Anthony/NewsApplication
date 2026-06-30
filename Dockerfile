# Use the official Python image as a base
FROM python:3.13-slim

# Set environment variables to prevent Python from writing .pyc files
# and to ensure output is sent straight to the terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the entire project into the container
COPY . .

# Collect static files (if any) and apply database migrations
RUN python manage.py collectstatic --noinput || true
RUN python manage.py migrate --noinput || true

# Expose port 8000 for the Django app
EXPOSE 8000

# Run the Django development server
# For production use, replace with: gunicorn config.wsgi:application --bind 0.0.0.0:8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
