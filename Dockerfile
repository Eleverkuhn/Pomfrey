FROM python:3.13.7-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --upgrade pip
RUN pip install .
COPY /django-api .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
