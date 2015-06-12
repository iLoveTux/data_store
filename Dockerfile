FROM fedora
MAINTAINER http://ilovetux.com

RUN dnf clean all
RUN dnf -y -4 update
RUN dnf -y -4 install python-pip python-cherrypy
RUN pip install data.store

ADD start_server.py /opt/

EXPOSE 8080

CMD [ "/usr/bin/python", "/opt/start_server.py" ]
