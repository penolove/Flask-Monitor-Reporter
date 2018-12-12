# MonitorReporter - flask

## used tools:
```
# js
canvasjs - v2.2

# python
flask
flask-admin
eyewitenss
```

## quick start
```
pyenv virtualenv monitor_36
pyenv activate monitor_36
pip install -r requirements.txt

# [Optional] if using Line set your env in env.list file
set -a
. ./env.list
set +a

# start App
export FLASK_APP=monitor_reporter
pip install -e .
flask run

# can see the example demo in http://127.0.0.1:5000/bar_chart/
# and db detail in http://127.0.0.1:5000/admin/
# the db config were set in monitor_reporter/__init__.py

```


## flask server with uwsgi and nginx example
with help https://github.com/tiangolo/uwsgi-nginx-flask-docker
```
docker build -t monitor_reporter -f Dockerfile .
docker run -d --name monitor_reporter_container -p 5000:80 --env-file env.list monitor_reporter 

# used db location /app/instance/example.sqlite
# used static location /app/monitor_reporter/static
```


## test line webhook with ngrok
line register webhook require https service
a quick solution is using ngrok: https://ngrok.com/
```
./ngrok http 5000
```