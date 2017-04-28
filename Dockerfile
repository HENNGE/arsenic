FROM ojii/arsenic-test:latest

ADD . /code

WORKDIR /code

RUN python3.6 -m venv test-env

RUN test-env/bin/pip install -U pip setuptools wheel

RUN test-env/bin/pip install . -r tests/requirements.txt

CMD ["test-env/bin/pytest", "--verbose"]
