from setuptools import setup, find_packages


setup(
    version='1.0.0.dev2',
    name='arsenic',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'attrs>=17.1.0',
        'structlog',
    ],
    license='APLv2',
    extras_require={
        'aiohttp': [
            'aiohttp>=2'
        ],
        'tornado': [
            'tornado>=4.5'
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6'
    ]
)
