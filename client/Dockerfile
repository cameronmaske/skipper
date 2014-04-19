FROM cmfatih/nodejs
MAINTAINER Cameron Maske "cam@trackmaven.com"

RUN apt-get install -y git
WORKDIR /code
RUN npm install -g bower gulp karma-cli phantomjs
RUN apt-get -y install libfreetype6-dev fontconfig

ADD run /usr/local/bin/run
RUN chmod +x /usr/local/bin/run

CMD ["/usr/local/bin/run"]