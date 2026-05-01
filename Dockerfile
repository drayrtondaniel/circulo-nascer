# ===========================================
# DR. AYRTON - CIRCULO NASCER
# Dockerfile - Render.com Ready
# ===========================================

FROM python:3.11-slim

LABEL maintainer="Sputnik Five"
LABEL description="Círculo Nascer - Dr. Ayrton Daniel"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=5000

WORKDIR /app

# Copiar requirements primeiro para cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretórios
RUN mkdir -p data/leads

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

CMD ["python", "app.py"]