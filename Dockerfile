FROM python:3.11-slim

WORKDIR /app

# Install system deps (important for pymongo + networking)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment
ENV PYTHONUNBUFFERED=1

EXPOSE 4000

# Production server
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:4000", "app:app"]