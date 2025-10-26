FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

WORKDIR /app

# Install system dependencies, then remove build tools to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libmagic1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove build-essential

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all relevant directories
COPY data/ ./data
COPY ui/ ./ui
COPY ingest/ ./ingest
COPY runtime/ ./runtime
COPY today/ ./today

# Set secure permissions
RUN chmod -R 755 /app/today

# Create a non-root user and switch to it
RUN useradd --create-home --home-dir /app appuser
USER appuser

EXPOSE 8501

ENV STREAMLIT_SERVER_HEADLESS=true

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "ui/app.py", "--server.address=0.0.0.0"]