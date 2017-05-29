FROM ubuntu:zesty

RUN apt-get update && apt-get install -y xvfb python3.6 python3.6-venv python3.6-dev firefox build-essential

COPY geckodriver-v0.16.1-linux64.tar.gz geckodriver-v0.16.1-linux64.tar.gz

RUN tar xzvf geckodriver-v0.16.1-linux64.tar.gz

RUN cp geckodriver /usr/local/bin/geckodriver

RUN chmod +x /usr/local/bin/geckodriver
