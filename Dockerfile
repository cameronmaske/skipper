FROM stackbrew/ubuntu:saucy
MAINTAINER Cameron Maske "cam@trackmaven.com"
RUN apt-get -y --fix-missing update

RUN apt-get install -y python python-pip python-dev python-yaml python-jinja2 python-apt python-pycurl git ssh sshpass sqlite3 libsqlite3-dev

WORKDIR /code/

ADD requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
ADD requirements-dev.txt /code/requirements-dev.txt
RUN pip install -r requirements-dev.txt

