Skipper
=======
[![Build Status](https://travis-ci.org/cameronmaske/skipper.svg?branch=master)](https://travis-ci.org/cameronmaske/skipper) [![Coverage Status](https://coveralls.io/repos/cameronmaske/skipper/badge.png)](https://coveralls.io/r/cameronmaske/skipper)

Build, deploy and orchestrate your application using Docker.

Quick start
-----------

With skipper [installed](#installation), let's deploy a simple web app.

In the app's directory, let's define a `skipper.yml`.

It describers...
  - `services` - the Docker containers that comprise our app.
  - `groups` - the instances that comprise our cluster.
  - `name` - the name of our application
  - `region` - the region our cluster runs on.


skipper.yml
```yml
name: "demo"
services:
    web:
        build: .
        scale: 1 # Optional, by default 1.
        ports:
            - "80:5000"
        repo:
            name: "cameronmaske/flask-web"
region: "us-east-1"
groups:
    web:
        size: "t1.micro"
        ports:
            public:
                - "80"
        services:
            - web
```

Now, let's create web app powered by Flask (A python micro framework) with a Dockerfile that runs it.

app.py
```python
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
FROM python:2.7
ADD . /code
WORKDIR /code
RUN pip install Flask
ADD app.py app.py
CMD python app.py
```

Now using skipper, we can deploy our service across the cluster. Deployments using skipper are comprised of three steps...

* `tag` - Build the service Docker image with an assigned tag.
* `push` - Uploads the tagged image to a Docker image registry.
* `deploy` - Coordinates with the desired host (currently only [AWS](aws.amazon.com) is supported) to launch or retrieve the required instances, and run the desired services.

When using skipper on a new project, you will be prompted for a various credentials required to communicate with the host (such as public/private ssh keys, or access/secret tokens). These are stored in a `.skippercfg` file, which should not be checked in too any source control.

```bash
$ skipper tag web:v1
Building web...
 ---> cdc18ed4ed6f
Step 1 : ADD . /code
 ---> a8bf1d374c29
Removing intermediate
...
Successfully built web...
$ skipper push web:v1
Sending image list
Pushing repository cameronmaske/flask-web (1 tags)
Pushing
Image already pushed, skipping
....
Image successfully pushed
Pushing tag for rev [e5bf1196d912] on {https://cdn-registry-1.docker.io/v1/repositories/cameronmaske/flask-web/tags/v1}
$ skipper deploy web:v1
Checking for instance [web_1].

As this is your first time running skipper, we need to store your some AWS Security Credentials.
Please visit https://console.aws.amazon.com/iam/home?#security_credential
Under Access Keys, click Create New Access Key.
Enter your Access Key ID: BCDHTEJEETTTRACEZ3GHQ
Enter your Secret Access Key: TC9hCTrsOWmLTAHECAGE192831BpPOd1lm90

Failed to find instance [web_1].

A KeyPair, consisting of an SSH public and private key is required for access to the cluster.
Please enter the an existing KeyPair's name, or enter a unique name for yourself: MyKeyPair
Please enter the path to a SSH public key: ~/.ssh/skipper.pub
Please enter the path to a SSH private key: ~/.ssh/skipper

Starting a new instance [web_1].

No token set for your etcd cluster.
Please visit https://discovery.etcd.io/new to generate a new one, or enter your existing one: https://discovery.etcd.io/49581751507f299928a34c8737f12

Successfully created instance [web_1].
Checking for service [web_1] on instance [web_1].
No existing service [web_1] found.
Creating service [web_1].
Successfully created service [web_1].
Deployment was successful.
```
Next we can check the app is running as expected.

```bash
$ skipper ps
+-------+---------+----------+---------------+---------+-------+
| uuid  |  state  | instance |      ip       | service | scale |
+-------+---------+----------+---------------+---------+-------+
| web_1 | running | web_1    | 54.165.238.25 | web     | 1     |
+-------+---------+----------+---------------+---------+-------+
$ curl 54.165.238.25
Hello World! v1
```

To ship a new version, we once again follow the three steps of `tag`, `push` and `deploy`.

```bash
$ # Replace v1 with v2.
$ sed -i -e 's/v1/v2/g' app.py
$ cat app.py | grep Hello World
    return "Hello World! v2"
$ skipper tag web:v2
$ skipper push web:v2
$ skipper deploy web:v2
$ curl 54.165.238.25
Hello World! v2
```


## Installation

Requires [Docker](http://www.docker.com) to be installed.

Docker has guides for [Ubuntu](http://docs.docker.io/en/latest/installation/ubuntulinux/) and [other platforms](http://docs.docker.io/en/latest/installation/) in their documentation. If you're on OS X, you can use [docker-osx](https://github.com/noplay/docker-osx):

Skipper can be installed as a Python package using...

```bash
$ sudo pip install -U skipper
```

## Documentation

Skipper is built on top of [Docker](https://www.docker.com/) and [CoreOS](https://coreos.com/). Using CoreOS's etcd and fleet services simplifies cluster management and container orchestration.
Unlike other PaaS that use Git (such as Heroku) as their mechanism to push and deploy applications, skipper moves that responsibility to Docker. Using Docker, you tag, push and deploy images across your cluster.
Currently the only host supported is [AWS](http://aws.amazon.com/) but other host support, starting with [DigitalOcean](https://coreos.com/blog/digital-ocean-supports-coreos/) is planned.

### skipper.yml

The `skipper.yml` contains all the information required to build, tag and deploy docker containers across your desired cluster.

```yml
name: demo
services:
    web:
        build: .
        scale: 1
        ports:
            - "80:5000"
        repo:
            name: "cameronmaske/flask-web"
region: "us-east-1"
groups:
    web:
        size: "t1.micro"
        scale: 2
        ports:
            public:
                - "80"
        services:
            - web
```

#### name (required)
Every project needs a name. This is used to identify which instances are project specific on a host.

#### region
```yml
region: "ap-northeast-1"
region: "us-east-1"
```

Which [Amazon EC2 region](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html) should I launch instances on? Defaults to "us-east-1".

**Only a single region is currently supported**.

#### services
Services define the components that make up your app.

##### repo (required)
```yml
repo:
    name: "cameronmaske/node-app"
    registry: "index.docker.io"
```

Points to a repo to upload and/or pull a Docker images from. If a registry is not included, defaults to the official [Docker Hub Registry](https://registry.hub.docker.com/).

**Currently only public registries are supported**.

##### build
```yml
build: folder/another/web
build: .
```
Path to a directory containing a Dockerfile to build the image off.

##### scale
```yml
scale: 1
scale: 10
```
Determines how many containers should be run for each service on each desired instance.

##### ports
```yml
ports:
    - "80:5000"
    - "80"
```
Exposes ports on a service's containers. Takes the format of `HOST:CONTAINER`. Either specify both ports, or just a container port (the host port is chosen at random).

#### groups
Groups define the instances that make up your cluster.

##### size
```
size: "t1.micro"
size: "m2.2xlarge"
```
What [AWS EC2 instance type](http://aws.amazon.com/ec2/instance-types/) should be used for instances belonging to this group?

##### ports
```
ports:
    public:
        - "80"
        - "443"
```
What ports should be exposed publicly?

##### services
```
services:
    - redis
    - web
```
What services should run on instances associated with the group?

##### scale
```
scale: 1
scale: 10
```
How many instances are required to make up the group?

### .skippercfg
Stores sensitive data required for skipper, such as AWS credentials. **Make sure this is not publicly exposed**

### CLI

Each of skipper's commands can be run with `--help` to reveal more information about what they do.

```
$ skipper --help
Usage: skipper [OPTIONS] COMMAND [ARGS]...

  A docker orchestration tool that allows you to easily
  deploy and manage your applications.

Options:
  --silent   Suppress logging messages.
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  clean      Removes older images locally for a services.
  deploy     Deploy services across the cluster.
  instances  Manages instances.
  ps         List all services running across the cluster.
  push       Push tagged services to their registries.
  remove     Remove a running service by uuid.
  tag        Build and tag services.
```

## Roadmap
Below is a outline of the feature set desired for *1.0*.

* Better documentation .
* Environment variables (cluster wide and service specific).
* Logging.
* Linking containers.
* Linking instances privately.
* DigitalOcean Support.
* Multi region support.
* Private repo support.
* Team and multiple user support.

## Inspiration
Heavily inspired by [Fig](https://github.com/docker/fig) and [head-in-the-clouds](https://github.com/andreasjansson/head-in-the-clouds).

## Contact
For bugs, please open an issue on [GitHub](https://github.com/cameronmaske/skipper).
If you have any comments, thoughts or ideas for skipper, feel free to also open an [issue](https://github.com/cameronmaske/skipper), [tweet me](http://www.twitter.com/cameronmaske) or drop me an [email](mailto:cameronmaske@gmail.com).
