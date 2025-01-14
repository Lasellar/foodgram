FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
CMD ["gunicorn", "backend.wsgi:application", "--bind", "127.0.0.1:8080"]