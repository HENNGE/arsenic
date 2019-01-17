import os
from setuptools import setup, find_packages

with open(os.path.relpath(f"{__file__}/../README.md")) as f:
    readme = f.read()

setup(
    version="1.0.0.dev8",
    name="arsenic",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["attrs>=17.1.0", "structlog", "aiohttp>=2"],
    entry_points={
        "console_scripts": [
            "arsenic-check-ie11 = arsenic.helpers:check_ie11_environment_cli",
            "arsenic-configure-ie11 = arsenic.helpers:configure_ie11_environment_cli",
        ]
    },
    author="Jonas Obrist",
    author_email="ojiidotch@gmail.com",
    description="Async Webdriver",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/HDE/arsenic",
    project_urls={
        "Documentation": "https://arsenic.readthedocs.io/en/latest/",
        "Code": "https://github.com/HDE/arsenic",
        "Issue tracker": "https://github.com/HDE/arsenic/issues",
    },
    license="APLv2",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
