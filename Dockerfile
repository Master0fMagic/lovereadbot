FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip config set global.target /app
RUN pip install -t requirements.txt

COPY . .

# run app
CMD ["python", "main.py"]