FROM ojii/arsenic-test:latest

ADD setup.py /code/setup.py
ADD pytest.ini /code/pytest.ini
ADD src /code/src/
ADD tests /code/tests/
ADD docs /code/docs/

WORKDIR /code

RUN python3.6 -m venv test-env

RUN test-env/bin/pip install -U pip setuptools wheel

RUN test-env/bin/pip install . -r tests/requirements.txt

RUN find . -regex '.*__pycache__.*' -delete

CMD xvfb-run test-env/bin/pytest --verbose
