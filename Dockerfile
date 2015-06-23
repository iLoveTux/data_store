FROM fedora
MAINTAINER http://ilovetux.com

# RUN dnf clean all
RUN dnf -y -4 update
RUN dnf -y -4 install python-pip wget git
RUN pip install cherrypy

RUN cd /opt/ && git clone https://github.com/ilovetux/data_store 
RUN wget -O /opt/data_store/bottle.py http://bottlepy.org/bottle.py 

RUN dnf remove -y wget git

EXPOSE 8080

CMD [ "/usr/bin/python", "/opt/data_store/start_server.py" ]
