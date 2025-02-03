FROM python:3.12-slim

WORKDIR /app

COPY . . 

RUN pip install -r requirements.txt

EXPOSE 8002 

CMD [ "python", "main.py" ]