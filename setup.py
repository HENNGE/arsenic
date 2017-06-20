from setuptools import setup, find_packages


setup(
    version='1.0.0.dev4',
    name='arsenic',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'attrs>=17.1.0',
        'structlog',
        'aiohttp>=2',
    ],
    license='APLv2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6'
    ]
)
