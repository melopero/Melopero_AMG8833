#!/usr/bin/python
import setuptools

setuptools.setup(
    name="melopero_amg8833",
    version="0.2.1",
    description="A module to easily access Melopero's AMG8833 sensor's features",
    url="https://github.com/melopero/Melopero_AMG8833/tree/master/module",
    author="Melopero",
    author_email="info@melopero.com",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
    ],
    install_requires=["smbus2>=0.4"],
)

