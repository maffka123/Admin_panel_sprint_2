FROM python:3.7
VOLUME /home
WORKDIR /home
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
COPY requirements.txt /home/requirements.txt
RUN pip3 install -r requirements.txt