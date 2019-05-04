FROM python:3.7-alpine


RUN mkdir /app
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT [ "celery" ] 
CMD [ "-A", "enttodevice", "worker", "-l", "info","-Q", "p2d"]
