import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="robovac",
    version="0.0.6",
    author="BnMcG",
    author_email="ben@bmagee.com",
    description="Python API for communicating with Eufy RoboVac 11c devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bnmcg/pyrobovac",
    packages=setuptools.find_packages(),
    install_requires=[
        'protobuf',
        'pycryptodome',
        'six'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
