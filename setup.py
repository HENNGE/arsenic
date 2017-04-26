from setuptools import setup, find_packages


setup(
    version='0.1',
    name='arsenic',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'attrs'
    ],
    extras_require={
        'aiohttp': [
            'aiohttp>=2'
        ],
        'tornado': [
            'tornado>=4.5'
        ],
        'twisted': [
            'twisted>=17'
        ]
    },
)
