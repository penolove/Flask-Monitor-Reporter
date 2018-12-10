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
docker build -t myimage -f Dockerfile .
docker run -d --name mycontainer -p 80:80 myimage
```