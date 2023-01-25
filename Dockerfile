FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get upgrade -y && apt-get install -y libsqlite3-dev libpq-dev python-dev build-essential python3-dev python2.7-dev libldap2-dev libsasl2-dev ldap-utils tox lcov valgrind
RUN pip install -U pip setuptools

COPY requirements.txt /code/
RUN pip install -r /code/requirements.txt

ADD . /code/
EXPOSE 8000