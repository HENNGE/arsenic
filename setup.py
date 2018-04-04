from setuptools import setup, find_packages


setup(
    version='1.0.0.dev7',
    name='arsenic',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'attrs>=17.1.0',
        'structlog',
        'aiohttp>=2',
    ],
    license='APLv2',
    entry_points={
        'console_scripts': [
            'arsenic-check-ie11 = arsenic.helpers:check_ie11_environment_cli',
            'arsenic-configure-ie11 = arsenic.helpers:configure_ie11_environment_cli',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6'
    ]
)
