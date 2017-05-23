from setuptools import setup, find_packages


setup(
    version='0.1',
    name='arsenic',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'attrs',
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
