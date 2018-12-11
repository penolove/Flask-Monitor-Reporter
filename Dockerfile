FROM tiangolo/uwsgi-nginx-flask:python3.6

ENV STATIC_PATH /app/monitor_reporter/static
ENV NGINX_WORKER_PROCESSES 3

RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    tmux 

# copy monitor-reporter into image as app
COPY . /app
RUN pip install -r /app/requirements.txt