FROM ubuntu:artful

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get install -y wget software-properties-common && \
  add-apt-repository ppa:mozillateam/firefox-next && \
  wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
  echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
  apt-get update && \
  apt-get install -y \
    python3.6 \
    python3.6-venv \
    python3.6-dev \
    build-essential \
    wget \
    unzip \
    firefox \
    libfontconfig \
    google-chrome-stable && \
  rm -rf /var/lib/apt/lists/*

ARG GECKODRIVER_VERSION=0.20.0
ARG CHROMEDRIVER_VERSION=2.37
ARG PHANTOMJS_VERSION=phantomjs-1.9.8-linux-x86_64

RUN wget --no-verbose -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
  && rm -rf /opt/chromedriver \
  && unzip /tmp/chromedriver.zip -d /opt/ \
  && rm /tmp/chromedriver.zip \
  && chmod 755 /opt/chromedriver \
  && ln -fs /opt/chromedriver /usr/local/bin/chromedriver

RUN wget --no-verbose -O /tmp/BrowserStackLocal.zip https://www.browserstack.com/browserstack-local/BrowserStackLocal-linux-x64.zip \
  && unzip /tmp/BrowserStackLocal.zip BrowserStackLocal -d /opt/ \
  && rm /tmp/BrowserStackLocal.zip \
  && chmod 755 /opt/BrowserStackLocal \
  && ln -fs /opt/BrowserStackLocal /usr/local/bin/BrowserStackLocal

RUN wget --no-verbose -O /tmp/phantomjs.tar.bz2 https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOMJS_VERSION.tar.bz2 \
  && tar -xf /tmp/phantomjs.tar.bz2 -C /opt/ \
  && rm /tmp/phantomjs.tar.bz2 \
  && chmod 755 /opt/$PHANTOMJS_VERSION/bin/phantomjs \
  && ln -fs /opt/$PHANTOMJS_VERSION/bin/phantomjs /usr/local/bin/phantomjs

RUN wget --no-verbose -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz \
  && rm -rf /opt/geckodriver \
  && tar -C /opt -zxf /tmp/geckodriver.tar.gz \
  && rm /tmp/geckodriver.tar.gz \
  && mv /opt/geckodriver /opt/geckodriver-$GECKODRIVER_VERSION \
  && chmod 755 /opt/geckodriver-$GECKODRIVER_VERSION \
  && ln -fs /opt/geckodriver-$GECKODRIVER_VERSION /usr/local/bin/geckodriver
