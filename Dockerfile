FROM python:3.12.8

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt


RUN useradd -u 1000 fastapi_user
USER fastapi_user



CMD ["python", "main.py"]
