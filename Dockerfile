FROM django:1.9-python2
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt-get update --fix-missing && apt-get -y install openssh-client
RUN adduser --disabled-password --gecos '' myuser