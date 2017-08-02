#FROM python:3.5.2
#
#ENV src /backend-src
#
#RUN apt-get update
#RUN pip install --upgrade pip
#
#RUN rm ${src} -rf
#COPY . ${src}
#WORKDIR ${src}
#
#RUN rm ${src}/sales_platform/migrations -rf
#RUN pip install -r requirements.txt
#
##RUN python3.5 ${src}/manage.py runserver 0.0.0.0:8888

FROM python:3.5.2
ENV src /backend-src

RUN apt-get update
#RUN apt-get install --upgrade pip
RUN apt-get install -y python-pip python-dev libmysqlclient-dev 
# Specify your own RUN commands here (e.g. RUN apt-get install -y nano)
# RUN rm ${src} -rf
COPY . ${src}
WORKDIR ${src}

RUN pip install -r requirements.txt
#RUN rm ${src}/sales_platform/migrations -rf
#RUN python3.5 ${src}/manage.py runserver 0.0.0.0:8888


