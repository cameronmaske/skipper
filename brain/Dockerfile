FROM stackbrew/ubuntu:saucy
MAINTAINER Cameron Maske "cam@trackmaven.com"
RUN apt-get -y --fix-missing update

RUN apt-get install -y python python-pip python-dev python-yaml python-jinja2 python-apt python-pycurl git ssh sshpass sqlite3 libsqlite3-dev

ADD requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

WORKDIR /code/

CMD python manage.py runserver 0.0.0.0:8000