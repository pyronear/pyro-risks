web: pip install -e . && pip install -r requirements-app.txt && gunicorn --workers 1 -b 0.0.0.0:${PORT:-5000} --chdir ./app main:server
