#!/usr/bin/env python3

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
        'browserstack-ie',
        dockerfile='tests/dockerfiles/browserstack',
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
import sys
from typing import List, Tuple, Optional, Dict

import attr


@attr.s
class Step:
    name: str = attr.ib()
    setup: List[str] = attr.ib()
    run: List[str] = attr.ib()


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


def step(name, *, dockerfile=None, **env):
    return Step(
        name,
        *_build_commands(name, dockerfile, env)
    )


def _build_commands(name: str, dockerfile: Optional[str], env: Dict[str, str]) -> Tuple[List[str], List[str]]:
    # use f-strings everywhere for nice indent
    dockerfile = dockerfile or f'tests/dockerfiles/{name}'
    return [
        f'      - run:',
        f'          name: Setup {name} ',
        f'          command: |',
        f'            docker build \\',
        f'            --tag {name} \\',
        f'            --file {dockerfile} \\',
        f'            .',
    ], [
        f'      - run:',
        f'          name: Run {name} ',
        f'          command: |',
        f'            docker run \\',
    ] + list(_build_env(env)) + [
        f'            {name} \\'
    ]


def _build_env(env):
    for key, value in env.items():
        yield f'              --env {key}={value} \\'


STEPS = list(define_steps())

TASK_PREAMBLE = [
    '    <<: *defaults',
    '    steps:',
    '      - setup_remote_docker:',
    '          reusable: true',
    '          exclusive: true',
    '      - checkout',
]

COMMON_SETUP = [
    '      - run:',
    '          name: Build base image',
    '          command: |',
    '            docker build \\',
    '            --tag base:1.0 \\',
    '            --file tests/dockerfiles/base \\',
    '            .'
]

PREAMBLE = [
    'version: 2',
    'defaults: &defaults',
    '  working_directory: /home/',
    '  docker:',
    '    - image: docker:latest',
    'jobs:',
    '  build:',
] + TASK_PREAMBLE + COMMON_SETUP

SETUP_TASK = [
    '  setup:',
] + TASK_PREAMBLE + COMMON_SETUP

WORKFLOWS_PREAMBLE = [
    'workflows:',
    '  version: 2',
    '  build-and-deploy:',
    '    jobs:',
    '      - setup'
]


def feed(itr, target):
    for thing in itr:
        target.write(f'{thing}\n')


def generate(target):
    feed(PREAMBLE, target)
    for step in STEPS:
        feed(step.setup, target)
    for step in STEPS:
        feed(step.run, target)
    feed(SETUP_TASK, target)
    for step in STEPS:
        feed(step.setup, target)
    for step in STEPS:
        feed([f'  {step.name}:'] + TASK_PREAMBLE + step.run, target)
    feed(WORKFLOWS_PREAMBLE, target)
    for step in STEPS:
        feed([
            f'      - {step.name}:',
            f'          requires:',
            f'            - setup'
        ], target)

if __name__ == '__main__':
    generate(sys.stdout)
