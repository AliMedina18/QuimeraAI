# Dockerfile para Quimera Backend
# Deploy target: Google Cloud Run
#
# Por qué python:3.12-slim:
#   - 'slim' excluye compiladores y librerías de desarrollo (~400MB menos)
#   - La imagen final es ~300MB vs ~700MB con la imagen completa
#   - Cloud Run cobra por recursos usados al arrancar: imagen pequeña = arranque más rápido
#
# Por qué no Alpine:
#   - colour-science y otras librerías científicas tienen dependencias C que
#     no compilan bien en Alpine (musl libc). debian/slim es más compatible.

FROM python:3.12-slim

# Instalar Node.js para validacion de sintaxis JSX (@babel/parser)
# Se usa en step3_generate._validate_react_syntax()
RUN apt-get update && \
    apt-get install -y nodejs npm --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Metadatos de la imagen
LABEL maintainer="Alicia Medina <aliciamedina@k11technologies.com>"
LABEL project="quimera-ai"
LABEL description="Agente de IA para diseño visual — Motor de Evaluación Estética"

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements primero (antes del código fuente).
# Docker cachea cada COPY por separado. Si solo cambia el código (no requirements),
# el paso RUN pip install no se re-ejecuta, ahorrando 2-3 minutos de build.
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Instalar dependencias Node.js (solo @babel/parser para validacion JSX)
RUN npm install --production

# Cloud Run inyecta la variable PORT en el contenedor.
# Siempre es 8080, pero la hacemos configurable por si acaso.
ENV PORT=8080

# Exponer el puerto (documentación, no abre el firewall)
EXPOSE 8080

# Health check: Cloud Run verifica este endpoint cada 30s.
# Si falla 3 veces seguidas, reinicia el contenedor.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Comando de arranque
# --host 0.0.0.0: escuchar en todas las interfaces (necesario en contenedor)
# --port $PORT: usar el puerto que inyecta Cloud Run
# Sin --reload: en producción no queremos que uvicorn reinicie al detectar cambios
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
