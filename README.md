# Skipper
[![Build Status](https://travis-ci.org/cameronmaske/skipper.svg?branch=master)](https://travis-ci.org/cameronmaske/skipper)
[![Coverage Status](https://coveralls.io/repos/cameronmaske/skipper/badge.png)](https://coveralls.io/r/cameronmaske/skipper)

Skipper is a docker orchestration tool.

Currently a work in progress. Won't work yet.

## Example

Let's run through an example deployment of a simple flask app.

skipper.yml
```
name: demo
groups:
    web:
        size: m1.small
        loadbalance:
            - "80:80"
        scale: 2
        regions:
            - us-east-1
            - us-west-1
services:
    web:
        build: .
        loadbalance:
            - "80:5000"
        scale: 2
        test: "python manage.py tests"
        repo:
            name: cameronmaske/flask-web
```

app.py
```
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World! v1"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

Dockerfile
```
FROM orchardup/python:2.7
ADD . /code
WORKDIR /code
RUN pip install Flask
ADD app.py app.py
CMD python app.py
```

Now let's run skipper.

```
$ skipper deploy
As this is your first time running skipper, we need to store your some AWS Security Credentials.
Please visit https://console.aws.amazon.com/iam/home?#security_credential
Under Access Keys, click Create New Access Key.

Enter your Access Key ID: AKIAJ3991836LH65ETJHQ
Enter your Secret Access Key:
GGFEDARHe--1[23odHvtHenLnfX

Great, these are now stored in skipper.json. Make sure you do not include this is any source control.

No existing EC2 Key Pairs can be found for demo. A new one will be generated and stored in skipper.json.

Checking index.docker.io for cameronmaske/flask-web.
No existing builds can be found for the web service.
Building web...
Successfully built web:v1
Pushing web:v1 to cameronmaske/flask-web:v1...
Successfully pushed web:v1

No web instances can be found for demo.
[1/2] Bootstrapping web instance.
[1/2] Installing docker.
[1/2] Installing load balancer.
[1/2] Successfully bootstrapped web instance.
[2/2] Bootstrapping web instance.
[2/2] Installing docker.
[2/2] Installing load balancer.
[2/2] Successfully bootstrapped web instance.
All instances are up and running.

Deploying web:v1 to instance web
[1/2] Pulling web:v1
[1/2] Running 2x web:v1
[1/2] Configuring load balancer 80 -> 5000 for 2x web:v1
[2/2] Pulling web:v1
[2/2] Running 2x web:v1
[2/2] Configuring load balancer 80 -> 5000 for 2x web:v1
All services are successfully deployed.

Configuring load balancer 80 -> 80 for web instance.
Successfully configured load balancer.

Deployment was successful.
```

Now let's ship a new version.
```
$ # Replace v1 with v2.
$ sed -i -e 's/v1/v2/g' app.py
$ cat app.py | grep Hello World
    return "Hello World! v2"
$ git commit -am "v2"
$ skipper deploy

Checking index.docker.io for cameronmaske/flask-web.
Outdated build found for the web service.
Building web...
Successfully built web:v2
Pushing web:v2 to cameronmaske/flask-web:v2...
Successfully pushed web:v2

Deploying web:v2 to instance web
[1/2] Pulling web:v2
[1/2] Running 2x web:v2
[1/2] Configuring load balancer 80 -> 5000 for 2x web:v2
[1/2] Stopping 2x web:v1
[2/2] Pulling web:v2
[2/2] Running 2x web:v2
[2/2] Configuring load balancer 80 -> 5000 for 2x web:v2
[2/2] Stopping 2x web:v1

All services are successfully deployed.
```


Heavily inspired by [Fig](https://github.com/orchardup/fig) and [head-in-the-clouds](https://github.com/andreasjansson/head-in-the-clouds).