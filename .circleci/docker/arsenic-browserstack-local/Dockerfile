FROM alpine:3.6

RUN apk add --no-cache wget unzip ca-certificates \
  && update-ca-certificates

RUN wget --no-verbose -O /tmp/BrowserStackLocal.zip https://www.browserstack.com/browserstack-local/BrowserStackLocal-linux-x64.zip \
  && unzip -o /tmp/BrowserStackLocal.zip BrowserStackLocal -d /opt/ \
  && rm /tmp/BrowserStackLocal.zip \
  && chmod 755 /opt/BrowserStackLocal

ENTRYPOINT /opt/BrowserStackLocal
