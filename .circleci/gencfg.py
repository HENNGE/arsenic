#!/usr/bin/env python3
import json


def define_steps():
    yield step(
        'unit',
        DOCS_DIR='/code/docs/',
        SPHINXBUILD='/code/test-env/bin/sphinx-build',
    )
    yield step(
        'phantomjs',
        ARSENIC_SERVICE='PhantomJS',
        ARSENIC_BROWSER='PhantomJS',
    )
    yield step(
        'geckodriver',
        ARSENIC_SERVICE='Geckodriver',
        ARSENIC_BROWSER='Firefox',
    )
    yield step(
        'chromedriver',
        ARSENIC_SERVICE='Chromedriver',
        ARSENIC_BROWSER='Chrome?{qs}'.format(
            qs=urlencode({
                'chromeOptions': json.dumps({
                    'args': ['--headless', '--disable-gpu', '--no-sandbox']
                })
            })
        ),
    )
    yield step(
        'browserstack-ie',
        service='test-browserstack',
        ARSENIC_SERVICE='"Remote?url=http://${BROWSERSTACK_USERNAME}:${BROWSERSTACK_API_KEY}@hub.browserstack.com:80/wd/hub"',
        ARSENIC_BROWSER=browser(
            'InternetExplorer',
            version='11.0',
            resolution='1024x768',
            os_version='7',
            browser_version='11.0',
            browserstack={
                'local': True,
                'localIdentifier': '${CIRCLE_SHA1}',
            },
            os='Windows',
            browser='IE',
            project='arsenic',
            build='${CIRCLE_SHA1}-${CIRCLE_BUILD_NUM}-IE',

        ),
        BROWSERSTACK_LOCAL_IDENTIFIER='"${CIRCLE_SHA1}"',
        BROWSERSTACK_API_KEY='"${BROWSERSTACK_API_KEY}"',
    )


# HERE BE DRAGONS
from urllib.parse import urlencode


def browser(name, **options):
    if options:
        params = {}
        for key, value in options.items():
            for query_key, query_value in _encode_browser_param(key, value):
                params[query_key] = query_value
        qs = urlencode(params, safe='{}$')
        return f'"{name}?{qs}"'
    else:
        return name


def _encode_browser_param(key, value):
    if value is True:
        yield key, ''
    elif isinstance(value, dict):
        for sub_key, sub_value in value.items():
            yield from _encode_browser_param(f'{key}.{sub_key}', sub_value)
    else:
        yield key, value


def step(name, *, service=None, **env):
    return (
        name,
        '\n'.join(_build_command(name, service, env))
    )


def _build_command(name, service, env):
    # use f-strings everywhere for nice indent
    service = service or f'test-{name}'
    yield f'      - run:'
    yield f'          name: Run {name} tests'
    yield f'          command: |'
    yield f'            docker-compose \\'
    yield f'              run \\'
    yield from _build_env(env)
    yield f'              --rm \\'
    yield f'              {service}'


def _build_env(env):
    for key, value in env.items():
        yield f'              -e {key}={value} \\'


STEPS = list(define_steps())

PREAMBLE = '''version: 2
defaults: &defaults
  working_directory: /home/
  docker:
    - image: docker/compose:1.9.0
jobs:
  build:
    <<: *defaults
    steps:
      - setup_remote_docker:
          reusable: true
          exclusive: true
      - checkout
      - run: docker-compose pull
      - run: docker-compose build'''

SETUP = '''      - run: docker-compose pull
      - run: docker-compose build'''

COMMON_SETUP = '''    <<: *defaults
    steps:
      - setup_remote_docker:
          reusable: true
          exclusive: true
      - checkout'''

WORKFLOWS_PREAMBLE = '''workflows:
  version: 2
  build-and-deploy:
    jobs:
      - setup'''


def generate():
    print(PREAMBLE)
    for _, step in STEPS:
        print(step)
    print('  setup:')
    print(COMMON_SETUP)
    print('      - run: docker-compose pull')
    print('      - run: docker-compose build')
    for name, step in STEPS:
        print(f'  {name}:')
        print(COMMON_SETUP)
        print(step)
    print(WORKFLOWS_PREAMBLE)
    for name, step in STEPS:
        print(f'      - {name}:')
        print('          requires:')
        print('            - setup')

if __name__ == '__main__':
    generate()
