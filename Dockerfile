FROM ubuntu:latest

COPY . /app

WORKDIR /app

RUN apt update && apt upgrade -y && \
    apt install python3 python3-pip npm -y

RUN pip3 install -r requirements.txt

RUN npm install bower -g

EXPOSE 8000

CMD ["/usr/bin/python3", "manage.py", "runserver", "0.0.0.0:8000"]