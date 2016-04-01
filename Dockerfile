FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
RUN apt-get update && apt-get -y install libffi-dev libxml2-dev libxslt1-dev graphviz libgraphviz-dev pkg-config libjpeg-dev libfreetype6-dev zlib1g-dev
RUN ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/ && ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/ && ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/
ADD . /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
