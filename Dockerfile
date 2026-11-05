# Dockerfile — Production Multi-Stage Build
# Stage 1: Build React 19 Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Backend Service
FROM python:3.9-slim AS runner
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code, data, and built frontend
COPY server.py .
COPY AI_Project_Tracker.xlsx .
COPY data/ ./data/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure database is migrated
RUN python data/migration.py

EXPOSE 8055

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8055/health || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8055", "--workers", "4"]

