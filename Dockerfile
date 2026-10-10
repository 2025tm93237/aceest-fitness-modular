FROM python:3.11-slim
WORKDIR /srv/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wsgi.py .
COPY pytest.ini .
COPY app/ app/
COPY tests/ tests/
RUN useradd --create-home --shell /bin/bash runtime && chown -R runtime:runtime /srv/app
ENV DB_PATH=/srv/app/aceest_fitness.db
USER runtime
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
