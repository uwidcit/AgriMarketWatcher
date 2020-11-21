import os
from setuptools import setup


setup(
    name='agrimarketwatcher',
    version='0.3',
    description='A service to receive price information from NAMDEVCO',
    url='https://github.com/uwidcit/AgriMarketWatcher',
    packages=['parse_rest'],
    package_data={"parse_rest": [os.path.join("cloudcode", "*", "*")]},
    install_requires=['six'],
    maintainer='Kyle De Freitas',
    maintainer_email='kyle.e.defreitas@gmail.com',
    classifiers=[
        "Programming Language :: Python :: 2.7",
    ]
)
