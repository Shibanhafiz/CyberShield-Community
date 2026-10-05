# CyberShield backend — multi-stage build.
# Build context MUST be the repository root (needs backend/ + ml/):
#   docker build -f backend/Dockerfile -t cybershield-backend .
# Stage 1 trains the ML model reproducibly from the versioned dev dataset,
# so the image never depends on a git-ignored *.joblib from the workstation.

FROM python:3.12-slim AS trainer
WORKDIR /build
COPY backend/requirements.txt .
# pandas/matplotlib are train-time only (kept out of the runtime image).
RUN pip install --no-cache-dir -r requirements.txt pandas matplotlib
COPY backend/ ./backend/
COPY ml/ ./ml/
RUN python ml/src/train.py && ls -la ml/models/scam_classifier.joblib

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN useradd -m -u 10001 appuser
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app/ ./backend/app/
COPY backend/scripts/ ./backend/scripts/
COPY backend/tests/ ./backend/tests/
COPY ml/src/ ./ml/src/
COPY --from=trainer /build/ml/models/scam_classifier.joblib ./ml/models/scam_classifier.joblib
COPY --from=trainer /build/ml/models/model_metadata.json ./ml/models/model_metadata.json
RUN chown -R appuser:appuser /app
USER appuser
WORKDIR /app/backend
EXPOSE 8001
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/api/ready')"
# All configuration via environment (see .env.example). Never bake secrets here.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
