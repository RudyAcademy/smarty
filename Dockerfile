# Smarty web app image -- the hosted, password-gated, mobile-friendly view
# of the same catalog/journal the desktop app uses. Does not include
# PySide6: smarty.web.app never imports smarty.ui.main_window/app.

FROM python:3.12-slim

WORKDIR /app

COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

COPY src/smarty ./smarty

# Persistent data lives here. On Render, mount a persistent disk at this
# path (paid plans only); without one, this directory is wiped on every
# redeploy/restart and the app falls back to re-seeding from the bundled
# catalog, losing any notes/status entered since the last deploy.
ENV SPARKY_LOCAL_ROOT=/data/smarty
RUN mkdir -p /data/smarty

EXPOSE 8000

# Render sets $PORT; default to 8000 for local/manual runs.
CMD ["sh", "-c", "uvicorn smarty.web.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
