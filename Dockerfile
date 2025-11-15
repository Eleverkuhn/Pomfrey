FROM python:3.13.7-slim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install .
ENV PYTHONPATH=app/django-api:/app
EXPOSE 8000
WORKDIR /app/django-api
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
