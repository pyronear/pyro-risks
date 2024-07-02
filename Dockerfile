FROM python:3.8.1

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy app requirements
COPY ./requirements.txt requirements.txt
COPY ./requirements-app.txt /usr/src/app/requirements-app.txt
COPY ./setup.py setup.py
COPY ./README.md README.md
COPY ./pyrorisks pyrorisks

# install dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y libspatialindex-dev python3-rtree && \
    pip install --upgrade pip setuptools wheel && \
    pip install -e . && \
    pip install -r /usr/src/app/requirements-app.txt && \
    mkdir /usr/src/app/app && \
    rm -rf /root/.cache/pip && \
    rm -rf /var/lib/apt/lists/*

# copy project
COPY app/ /usr/src/app/app/
