FROM python:3.13.7-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --upgrade pip
RUN pip install .
COPY . .
EXPOSE 8000
WORKDIR /app/src
